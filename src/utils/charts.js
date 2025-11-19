export function pieData(labels, values, colors){
  return {
    labels,
    datasets: [{
      data: values,
      backgroundColor: colors
    }]
  }
}

export function barData(labels, values, color){
  return {
    labels,
    datasets: [{
      label: "Count",
      data: values,
      backgroundColor: color
    }]
  }
}
