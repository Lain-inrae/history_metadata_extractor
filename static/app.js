
var content = document.getElementById("history_metadata_extractor_content") ;
document.getElementById("history_metadata_extractor_top").onclick = () => {
  content.scrollTo(0, 0) ;
} ;
document.getElementById("history_metadata_extractor_bottom").onclick = () => {
  content.scrollTo(0, content.scrollHeight) ;
} ;
var folded = false ;
document.getElementById("history_metadata_extractor_folder").onclick = (e) => {
  if (folded) {
    var func = (item) => item.classList.remove("d-none") ;
  } else {
    var func = (item) => item.classList.add("d-none") ;
  }
  Array.prototype.forEach.call(document.getElementsByClassName("history_metadata_extractor_table"), func) ; 
  folded = ! folded ;
} ;

var kawaii = false ;
document.getElementById("glitter-generator").onclick = (e) => {
  if (kawaii) {
    var func = (item) => item.classList.remove("kawaii") ;
  } else {
    var func = (item) => item.classList.add("kawaii") ;
  }
  Array.prototype.forEach.call(document.querySelectorAll("[class^=history_metadata_extractor_]"), func) ; 
  kawaii = ! kawaii ;
} ;

var show_deleted = true ;
document.getElementById("history_metadata_extractor_toggle_deleted").onclick = (e) => {
  show_deleted = !show_deleted ;
  if (show_deleted) {
    var func = (item) => item.classList.remove("d-none") ;
  } else {
    var func = (item) => item.classList.add("d-none") ;
  }
  Array.prototype.forEach.call(
    document.getElementsByClassName("history_metadata_extractor_deleted"),
    func
  ) ;
} ;

Array.prototype.forEach.call(document.getElementsByClassName(
  "history_metadata_extractor_h2"),
  (h2) => {
    var table = h2.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling ;
    h2.onclick = (e) => {
      if (table.classList.contains("d-none")) {
        table.classList.remove("d-none") ;
      } else {
        table.classList.add("d-none") ;
      }
    }
  }
)
