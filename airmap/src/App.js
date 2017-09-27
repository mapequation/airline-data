import React, { Component } from 'react';
import './App.css';
import Airmap from './Airmap';

class App extends Component {
  render() {
    return (
      <div className="App">
        <div className="App-header">
          <h2>Air traffic map</h2>
        </div>
        <Airmap />
      </div>
    );
  }
}

export default App;
