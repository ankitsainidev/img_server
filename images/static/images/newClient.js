var arr = []
var thumbinput = document.getElementById('id_thumbs');
function initialize(){
    var k = document.getElementsByClassName("no");
    for(var i=0;i<k.length; i++){
        if (k[i].checked){
            arr.push(k[i].id[k[i].id.length - 1]);
        }
    }
    thumbinput.value = arr.sort().join('');
}
initialize();
function validate(){
    if (arr.length==0){
        alert("You'll have to select atleast one drive.");
        return false;
    }
    return true;
}
function update(chbx){
    
    if (!chbx.checked){
        for( var i = 0; i < arr.length; i++){ 
            if ( arr[i] === chbx.id[chbx.id.length -1]) {
              arr.splice(i, 1); 
            }
         }
    }
    else{
        arr.push(chbx.id[chbx.id.length -1]);
    }
    thumbinput.value = arr.sort().join('');
}