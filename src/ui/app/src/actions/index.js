// import { ADD_ARTICLE } from "../constants/action-types";
// export const addArticle = article => ({ type: ADD_ARTICLE, payload: article });

import { BASE_URL } from '../constants/api'


export let startFrameworkEndpointsFetch = () => {
  return {
    type: "START_FRAMEWORK_ENDPOINTS_FETCH"
  }
}

export let endFrameworkEndpointsFetch = (framework) => {
  return {
    type: "END_FRAMEWORK_ENDPOINTS_FETCH",
    framework: framework,
  }
}

export let fetchFrameworkEndpoints = () => {
  let url = BASE_URL + '/api/framework/endpoints'
  // console.log("ffe")

  return (dispatch) => {
    // console.log("ffe dispatch")
    dispatch(startFrameworkEndpointsFetch())
    return fetch(url).then(
      (response) => {
        response.json().then((json) => dispatch(endFrameworkEndpointsFetch(json)))
      },
      (err) => {
        console.log(err);
      }
    )
  }
}
