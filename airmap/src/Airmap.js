import React, { Component } from 'react';
import './Airmap.css';
import * as d3 from 'd3';
import * as topojson from 'topojson';

global.d3 = d3;


    
const parseCluRow = (d, i) => {
  if (d[0][0] === '#') {
    return null;
  }
  return { node: d[0], cluster: +d[1], flow: Number(d[2]) };
};
const parseAirportsRow = (d => {
  d.lat = +d.LATITUDE;
  d.lng = +d.LONGITUDE;
  d.point = [d.lng, d.lat];
  return d;
})

class Airmap extends Component {
  
  onMountSvg = (el) => {
    this.svg = el;
  }
  
  componentDidMount() {
    this.drawChart();
  }
  
  shouldComponentUpdate() {
    return false; // This prevents future re-renders of this component
  }
  
  drawChart() {
    const width = 960;
    const height = 500;

    //Create SVG element and append map to the SVG
    const svg = d3.select("body")
      .append("svg")
      .attr("width", width)
      .attr("height", height);
    
    const g = svg.append('g');

    const zoomed = () => {
      g.style("stroke-width", 1.5 / d3.event.transform.k + "px");
      g.attr("transform", d3.event.transform);
    };

    // Click to zoom: https://bl.ocks.org/iamkevinv/0a24e9126cd2fa6b283c6f2d774b69a2
    
    // If the drag behavior prevents the default click,
    // also stop propagation so we don’t click-to-zoom.
    const stopped = () => {
      if (d3.event.defaultPrevented) d3.event.stopPropagation();
    };
    
    const projection = d3.geoAlbersUsa()
      .translate([width/2, height/2])    // translate to center of screen
      .scale([1000]);          // scale things down so see entire US
    
    const zoom = d3.zoom()
      .scaleExtent([1, 8])
      .on("zoom", zoomed);

    // Define path generator
    const path = d3.geoPath()        // path generator that will convert GeoJSON to SVG paths
           .projection(projection);  // tell path generator to use albersUsa projection
    // const projection = path.projection() || ((p) => p);
    
        // svg.call(zoom); // delete this line to disable free zooming
    
    const clusterColor = (cluster) => {
      return cluster < 10 ? d3.schemeCategory10[cluster] : '#cccccc';
    };
    
    const r = d3.scaleSqrt()
    .domain([0, 1])
    .range([2, 40]);
    
    d3.queue()
    // .defer(d3.json, 'https://d3js.org/us-10m.v1.json')
    // .defer(d3.json, 'https://bl.ocks.org/mbostock/raw/4090846/us.json')
    .defer(d3.json, '/us.json')
    .defer(d3.csv, '/airports.csv', parseAirportsRow)
    .defer(d3.text, '/2011_1_2_3_4_states_1.clu')
    // .defer(d3.text, '/2011_1_2_3_4_states_1_r25.clu')
    .await((error, us, airports, cluText) => {
      if (error) throw error;

      const dsv = d3.dsvFormat(' ');
      const clu = dsv.parseRows(cluText, parseCluRow);
      
      console.log('clu:', clu);
      console.log('clu item:', clu[0]);
      console.log('airports item:', airports[0]);

      const numClusters = d3.max(clu, d => d.cluster);
      console.log('numClusters:', numClusters);

      const nodeToAirport = {};
      airports.forEach(d => {
        nodeToAirport[d.AIRPORT_ID] = d;
      })

      clu.forEach(d => {
        d.airport = nodeToAirport[d.node];
        if (!d.airport) {
          console.log('Missing airport for node:', d.node);
        }
      })

      g.append("g")
        .attr("class", "states")
      .selectAll("path")
        .data(topojson.feature(us, us.objects.states).features)
      .enter().append("path")
        .attr("class", "state")
        .attr("d", path);
      
      g.append("path")
        .datum(topojson.mesh(us, us.objects.states, (a, b) => a !== b))
        .attr("class", "state-borders")
        .attr("d", path);
      

      svg.append('g')
        .attr('class', 'airports')
        .selectAll("circle")
        .data(clu)
        .enter()
        .append("circle")
        // .attr("cx", d => projection(d.airport.point)[0])
        // .attr("cy", d => projection(d.airport.point)[1])
        .attr("cx", d => {
          const p = projection(d.airport.point);
          if (!p) {
            // console.log('Projection error!:', d.airport.point, '->', p);
            return 0;
          }
          // console.log(d.airport.point);
          return p[0];
        })
        .attr("cy", d => {
          const p = projection(d.airport.point);
          if (!p) {
            // console.log('Projection error!:', d.airport.point, '->', p);
            return 0;
          }
          return p[1];
        })
        .attr("r", d => r(d.flow))
        .style("fill", d => clusterColor(d.cluster))
        .style("opacity", 0.85)	
    });
  }

  render() {
    return (
      <div className="Airmap">
      <svg ref={this.onMountSvg} />
      </div>
    );
  }
}

export default Airmap;
