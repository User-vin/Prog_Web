function openSide(){
    document.getElementById("sidebar").style.width = "250px";
}

function handleMousePos(event) {
    var mouseClickWidth = event.clientX;
    if(mouseClickWidth>=250){
          document.getElementById("sidebar").style.width= "0";
    }
}

document.addEventListener("click", handleMousePos);