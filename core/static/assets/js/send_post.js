function sendPost(csrf_token, url, POST_REQUEST, cb) {
	if(navigator.onLine){
	  var xhttp = new XMLHttpRequest();
	  var myObj;
	  xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			try {
				myObj = JSON.parse(this.responseText);
			}catch(err) {
				var myObj = {
					data:  this.responseText
				};
				//alert("Il parser JSON ha restituito un errore (" + err + ") mentre provava a contattare la pagina " + url + " \n Responso:" + this.responseText);
				console.log("Il parser JSON ha restituito errore");
			}
				cb(myObj);
			
		}else{
			cb("error", xhttp.status);
		}
	  };
	  xhttp.open("POST", url, true);
	  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	  xhttp.setRequestHeader("X-CSRFToken",csrf_token);
	  xhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

		var dataPost = JSON.stringify(POST_REQUEST);
		xhttp.send("data=" + dataPost);
		
	} else {
	  //alert('Impossibile eseguire la richiesta, connettersi ad internet');
	  cb("error", "Connessione internet assente");
	}
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
