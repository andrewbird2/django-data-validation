import * as React from 'react';
import Spinner from 'react-bootstrap/Spinner';

import {fetchCSRFInfo, fetchValidators} from "../data/api";
import {Status} from "../data/enums";
import {IValidator} from "../data/interfaces";
import App, {IApp} from "./app";
import {IModel} from "./model";


interface IAppList {
    [appLabel: string]: IApp,
}


/**
 * takes a flat list of Validators and converts it to a nested
 * structure (IAppList) that maps appLabels -> models -> validators
 */
function buildNestedValidatorSummary(validators: IValidator[]): IAppList {
    const result = {} as IAppList;

    for (const validator of validators) {
        if (!result.hasOwnProperty(validator.app_label)) {
            result[validator.app_label] = {
                appLabel: validator.app_label,
                status: Status.UNINITIALIZED,
                models: {}
            } as IApp;
        }
        const app = result[validator.app_label];

        if (!app.models.hasOwnProperty(validator.model_name)) {
            app.models[validator.model_name] = {
                appLabel: validator.app_label,
                modelName: validator.model_name,
                status: Status.UNINITIALIZED,
                validators: []
            } as IModel
        }
        app.models[validator.model_name].validators.push(validator);
    }

    // update the status for each App and Model level summary
    type HasStatus = {status: Status};
    const aggregateStatus = (parent: HasStatus, children: HasStatus[]) => {
        for (const child of children) {
            if (child.status === Status.PASSING &&
                parent.status === Status.UNINITIALIZED) {
                parent.status = Status.PASSING
            }
            else if (child.status === Status.FAILING) {
                parent.status = Status.FAILING ;
            }
            else if (child.status === Status.EXCEPTION) {
                parent.status = Status.EXCEPTION;
                break;
            }
        }
    }
    for (const app of Object.values(result)) {
        for (const model of Object.values(app.models)) {
            aggregateStatus(model, model.validators);
        }
        aggregateStatus(app, Object.values(app.models));
    }

    return result;
}


/**
 * A list of django apps and their data validation results
 */
export const AppList: React.FC = () => {
    const [validators, setValidators] = React.useState([] as IValidator[]);
    const [isLoading, setIsLoading] = React.useState(true);

    React.useEffect(() => {
        (async function() {await fetchCSRFInfo()})();
    }, []);

    React.useEffect(() => {
        (async function() {
            setIsLoading(true);
            await fetchValidators(setValidators).then();
            setIsLoading(false);
        })();
    }, []);

    const appList = buildNestedValidatorSummary(validators);

    if (isLoading) {
        return (
            <div style={{position: "relative"}}>
                <Spinner
                    animation="border" role="status" variant="primary"
                    style={{position: "absolute", left: "50%"}}
                />
            </div>
        );
    }
    return (
        <>
            <h2 style={{marginBottom: "10px", color: "#417690"}}> Data Validation Summary </h2>
             {
                Object.values(appList).map(app =>
                    <App
                        key={app.appLabel}
                        appLabel={app.appLabel}
                        status={app.status}
                        models={app.models}
                        setValidators={setValidators}
                    />
                )
            }
        </>
    );
}


export default AppList;
