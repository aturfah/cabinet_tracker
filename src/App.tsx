import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

// Point Eel web socket to the instance
export const eel = window.eel
eel.set_host( 'ws://localhost:8080' )

// Expose the `sayHelloJS` function to Python as `say_hello_js`
function sayHelloJS( x: any ) {
  console.log( 'Hello from ' + x )
}
// WARN: must use window.eel to keep parse-able eel.expose{...}
window.eel.expose( sayHelloJS, 'say_hello_js' )

// Test anonymous function when minimized. See https://github.com/samuelhwilliams/Eel/issues/363
function show_log(msg:string) {
  console.log(msg)
}
window.eel.expose(show_log, 'show_log')

// Test calling sayHelloJS, then call the corresponding Python function
sayHelloJS( 'Javascript World!' )
eel.say_hello_py( 'Javascript World!' )

// Set the default path. Would be a text input, but this is a basic example after all
const defPath = '~'

interface IAppState {
  message: string
  path: string
  displayCounts: boolean
  tableData: string[][]
}

export class App extends Component<{}, {}> {
  public state: IAppState = {
    message: `Click button to choose a random file from the user's system`,
    displayCounts: false,
    path: defPath,
    tableData: []
  }


  public flipItems = () => {
    this.setState({displayCounts: !this.state.displayCounts});
  }

  public getCabinets = () => {
    eel.get_cabinet_counts()((res: {data: string[][], dir: string}) => {
      console.log(res)
      this.setState({
        path: res.dir,
        tableData: res.data})
    })
  }

  public buildTable(total: boolean) {
    var tblRows: Object[] = [];

    this.state.tableData.forEach(function(x) {
      let trClass: string = "main";
      if (x[0] === " ") {
        if (total === false) {
          return;
        } else {
          trClass = "sub";
        }
      }
      tblRows.push(<tr className={trClass}>
        <td>{x[0]}</td>
        <td>{x[1]}</td>
        <td>{x[2]}</td>
      </tr>)
    })

    return <table>
      <thead>
        <tr>
          <th>Job ID</th>
          <th>Date/Unit ID</th>
          <th>Total Parts</th>
        </tr>
      </thead>
      <tbody>
        {tblRows}
      </tbody>
    </table>
  }

  public render() {
    return (
      <div className="App">
          <button className='App-button' onClick={this.getCabinets}>Load/Display Tables</button>
          <button className='App-button' onClick={this.flipItems}>{this.state.displayCounts ? "Hide Items" : "Show Items"}</button>
        <header className="App-header">
          <h2>Job Totals</h2>
          <p><b>Chosen Directory:</b> {this.state.path}</p>
          <div>
            {this.buildTable(this.state.displayCounts)}
          </div>
        </header>
      </div>
    );
  }
}

export default App;
