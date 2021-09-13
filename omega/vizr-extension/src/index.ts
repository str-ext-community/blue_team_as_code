import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { 
  INotebookTracker, 
  NotebookActions 
} from '@jupyterlab/notebook';
import { Buffer } from "buffer"

/**
 * Initialization data for the vizr-extension extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'vizr-extension:plugin',
  autoStart: true,
  optional: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebookTracker: INotebookTracker | null) => {
    console.log('JupyterLab extension vizr-extension is activated!');

    NotebookActions.executed.connect((_, action) => {
      const current = notebookTracker.currentWidget;
      const notebook = current.content;
      
      var DRC = false;
      var content = action.cell.model.toJSON()['source'] as string;
      let out = action.cell.model.toJSON()['outputs'] as Array<any>;
      out = out[0] 
      let k: keyof typeof out;
      for (k as String in out) {
        const v = out[k];
        if(String(k) == "text" && String(v).startsWith('#drc')){
          DRC = true;
          content = String(v);
          break;
        }
      }
    if (DRC){
        var activeindex = notebook.activeCellIndex
        let ar = content.split("\n");
        if(ar.length >= 2){
          // console.log('decoding b64 ...')
          let b64 = ar[1]; //.substring(1);
          let buff = Buffer.from(b64, 'base64');
          var arr = JSON.parse(buff.toString('utf-8')); //try catch
          if (Array.isArray(arr)){
            arr.forEach(function (item) {
              let k = Object.keys(item)[0];
              let code =  item[k];
              let activeCell = notebook.activeCell;
              NotebookActions.insertBelow(notebook);
              activeCell.model.value.text = code;                

              //change type to markdown
              if (k == "markdown"){
                notebook.activeCellIndex = notebook.activeCellIndex - 1;
                NotebookActions.changeCellType(notebook, k);
                notebook.activeCellIndex = notebook.activeCellIndex + 1;
              }
            });
            notebook.activeCellIndex = activeindex++;
            NotebookActions.renderAllMarkdown(notebook)
          } else {
            // console.log('not array ...')
          }
        }
      }
    });
  }
};

export default extension;