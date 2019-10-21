export const FindNotes = (notes, order_matters=false) => {
  function callback(string, fret, is_press) {
    return false
  }

  return Object.freeze(
    {
      callback,
    }
  )
}

