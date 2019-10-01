import * as action_types from "../constants/action-types";
import { BASE_URL } from '../constants/api.js'

import Frameworks from '../actions/framework_client'

const initialState = {
  frameworks: null,
  PlayerApi: {},
  MatchApi: {},
  game_modes_selected: ['squad-fpp', 'squad', 'duo-fpp', 'duo', 'solo-fpp', 'solo'],
  game_modes: [],
};


const appReducer = (state={}, action) => {
  if (action.start) {
    return state
  }

  return Object.assign({}, state, {
    [action.function]: fnReducer(state[action.function] ? state[action.function] : {}, action)
  })
}

const do_aggregation = (initial_data, new_data, aggregation_key) => {
  if (!initial_data) { return new_data }

  let filtered_new_data = new_data.filter((v) => {
      let matches = initial_data.filter((iv) => {
        return iv[aggregation_key] === v[aggregation_key]
      })
      return matches.length === 0
    })

 // console.log("filtered_new_data =", filtered_new_data)
  return initial_data.concat(filtered_new_data)
}

const fnReducer = (state={}, action) => {
  let data = action.payload;

  if (action.storage_key) {
    if (action.aggregate) {
      data = do_aggregation(state[action.storage_key], data, action.aggregate)
    }
    return Object.assign({}, state, {
      [action.storage_key]: data
    })
  } else {
    if (action.aggregate) {
      data = do_aggregation(state, data, action.aggregate)
    }
    // console.log(action, data)
    return data
  }
}

const rootReducer = (state = initialState, action) => {
  // console.log('action', action.type)
  switch (action.type) {

    case action_types.START_FRAMEWORK_ENDPOINTS_FETCH:
      return { ...state, frameworks: null };

    case action_types.END_FRAMEWORK_ENDPOINTS_FETCH:
      // console.log(action.framework)
      return { ...state, frameworks: new Frameworks(BASE_URL, action.framework) }

    case action_types.FRAMEWORK_FETCH:
      // console.log("framework fetch", action)
      return Object.assign({}, state, {
        [action.app]: appReducer(state[action.app] ? state[action.app] : {}, action)
      })

    case action_types.TOGGLE_GAME_MODE:
      let modes = []
      if (!state.game_modes_selected) {
        modes = state.MatchApi.game_modes
      } else {
        modes =  state.game_modes_selected
      }

      let i = modes.indexOf(action.game_mode)
      if (i >= 0) {
        return {...state, game_modes_selected: [
          ...modes.slice(0, i),
          ...modes.slice(i + 1)
        ]}
      } else {
        return {...state, game_modes_selected: modes.concat([action.game_mode])}
      }

    default:
      // console.log("Unknown action", action)
      return state
  }
};

export default rootReducer;
