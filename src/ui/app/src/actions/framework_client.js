import * as action_types from '../constants/action-types';

class Framework {
  constructor(base_url, data) {
    // console.log(data)
    Object.keys(data).filter((k) => {
      return (k[0] !== '_')
    }).map((k) => {
      let cmd = data[k]
      const whole_url = base_url + '/' + cmd['simple_url']
      this[k] = (context, framework_options) => {
        let storage_key = framework_options ? framework_options.storage_key : null
        let aggregate = framework_options ? framework_options.aggregate : null

        // console.log("Starting framework fn", cmd.app, cmd.function, context, storage_key)
        return (dispatch) => {
          // console.log("action start", dispatch)
          dispatch({
            type: action_types.FRAMEWORK_FETCH,
            app: cmd.app,
            function: cmd.function,
            storage_key: storage_key,
            payload: null,
            clear: false,
            start: true,
          })

          // console.log("posting ", JSON.stringify(context), "to", whole_url)
          fetch(whole_url, {
            method: 'POST',
            body: JSON.stringify(context),
            headers: {
              "Content-Type": "application/json; charset=utf-8",
            },
          }).then(
            (response) => {
              // console.log("response ok", response.ok)
              response.json().then(
                (json) => {
                  dispatch({
                    type: action_types.FRAMEWORK_FETCH,
                    payload: json,
                    storage_key: storage_key,
                    aggregate: aggregate,
                    app: cmd.app,
                    function: cmd.function,
                    start: false,
                  })
                }
              )
            },
            (err) => {
              console.log("ERROR!!", err);
            }
          )
        }
      }
      return true;
    })
  }
}

class Frameworks {
  constructor(base_url, framework_data) {
    // console.log(framework_data)
    Object.keys(framework_data).filter((k) => {
      return (k !== 'user')
    }).map((k) => {
      this[k] = new Framework(base_url, framework_data[k])
      return true;
    })
  }
}

export default Frameworks;
