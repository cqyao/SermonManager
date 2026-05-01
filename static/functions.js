function toggleMenu() {
  var x = document.getElementById("sideNav");
    if (x.style.width === "0px") {
      x.style.width = "50%"
    } else {
      x.style.width = "0px"
    }
}

function togglePopup() {
  var popup = document.getElementById("popup");
  if (popup.style.display === "block") {
    popup.style.display = "none" 
  } else {
    popup.style.display = "block"
  }
}