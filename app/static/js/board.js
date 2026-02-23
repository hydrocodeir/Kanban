(function(){
  function cleanupTybrty(){
    try{
      const scope = document.getElementById("boardColumnsContainer") || document.body;
      const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
      const toRemove = [];
      while(walker.nextNode()){
        const n = walker.currentNode;
        if(n && n.nodeValue && n.nodeValue && n.nodeValue.toLowerCase().includes("tybrty")){
          toRemove.push(n);
        }
      }
      toRemove.forEach(n=> n.parentNode && n.parentNode.removeChild(n));
    }catch(e){}
  }

  function scrollToRight(){
    try{
      const wrap = document.querySelector(".board-columns-wrap");
      if(!wrap) return;
      requestAnimationFrame(()=>{ wrap.scrollLeft = 0; });
    }catch(e){}
  }

  function updateCounts(){
    try{
      if(window.KanbanUI && typeof window.KanbanUI.updateCounts === "function"){
        window.KanbanUI.updateCounts();
      }else{
        document.querySelectorAll('.kanban-col').forEach((col)=>{
          const list = col.querySelector('.task-list');
          const count = list ? list.querySelectorAll('.task-card').length : 0;
          const badge = col.querySelector('.col-count');
          if(badge) badge.textContent = String(count);
        });
      }
    }catch(e){}
  }

  function reloadBoard(projectId){
    const root = document.getElementById("boardRoot");
    if(!root) return;
    htmx.ajax("GET", `/htmx/projects/${projectId}/board`, {target: "#boardRoot", swap: "innerHTML"});
  }

  function initSortable(){
    const lists = document.querySelectorAll(".task-list");
    if (!lists || lists.length === 0) return;

    const boardRoot = document.getElementById("boardRoot");
    const projectId = boardRoot ? boardRoot.getAttribute("data-project-id") : null;

    lists.forEach((el) => {
      if (el.dataset.sortableInit === "1") return;
      el.dataset.sortableInit = "1";

      new Sortable(el, {
        group: "tasks",
        animation: 150,
        ghostClass: "sortable-ghost",
        chosenClass: "sortable-chosen",
        dragClass: "sortable-drag",
        onEnd: function(evt){
          try{
            const item = evt.item;
            const taskId = item.getAttribute("data-task-id");
            const toColumnId = evt.to.getAttribute("data-column-id");
            const order = Array.from(evt.to.querySelectorAll(".task-card"))
              .map(x => x.getAttribute("data-task-id"))
              .join(",");
            if(!taskId || !toColumnId) return;

            // بلافاصله شمارنده‌ها آپدیت شوند
            updateCounts();

            htmx.ajax("PUT", `/htmx/tasks/${taskId}/move`, {
              values: { to_column_id: toColumnId, order: order },
              target: `#task-${taskId}`,
              swap: "outerHTML",
            });
          }catch(e){
            console.error(e);
          }
        }
      });
    });

    window.__kanbanReloadBoard = function(){
      if(projectId) reloadBoard(projectId);
    };
  }

  function initUI(root){
    try{
      if(window.KanbanUI && typeof window.KanbanUI.init === "function"){
        window.KanbanUI.init(root || document);
      }
    }catch(e){}
  }

  document.body.addEventListener("htmx:afterRequest", function(){
    updateCounts();
    cleanupTybrty();
  });

  document.body.addEventListener("htmx:afterSwap", function(evt){
    updateCounts();
    cleanupTybrty();
    initSortable();
    initUI(evt.target);

    // فقط وقتی برد دوباره لود شد، به سمت راست اسکرول کن
    try{
      const t = evt.target;
      if(t && (t.id === "boardRoot" || t.querySelector && t.querySelector(".board-columns-wrap"))){
        if(window.innerWidth > 768){ scrollToRight(); }
      }
    }catch(e){}
  });

  document.addEventListener("DOMContentLoaded", function(){
    updateCounts();
    cleanupTybrty();
    initSortable();
    initUI(document);
    if(window.innerWidth > 768){ scrollToRight(); }
  });
})();
