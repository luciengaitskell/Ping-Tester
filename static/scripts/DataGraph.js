function DataGraph(containerName) {
  this.dpsmean = []; // dataPoints
  this.dpsextreme = []; // dataPoints

  this.chart = new CanvasJS.Chart(containerName,{
    title :{
      text: "Ping to 8.8.8.8"
    },
    axisX:{
      valueFormatString: "HH:mm" ,
      labelAngle: -50
    },
    axisY:{
      minimum: -1,
      maximum: 300
    },
    data: [
      {
      type: "line",
      showInLegend: true,
      markerType: "square",
      legendText: "Mean Ping",
      dataPoints: this.dpsmean
    },
    {
      type: "line",
      showInLegend: true,
      legendText: "Extreme Ping",
      dataPoints: this.dpsextreme
    }]
  });
}

DataGraph.prototype.pushDpsData = function(data) {
  console.log(data);
  this.dpsmean.push({
    x: new Date(data.time*1000),
    y: data.mean
  });
  this.dpsextreme.push({
    x: new Date(data.time*1000),
    y: data.extreme
  });
}

DataGraph.prototype.render = function(){
  this.chart.render();
}
