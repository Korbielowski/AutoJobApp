function closeAlert(){
    const alertContainer = document.getElementById("alert-container");
    const alertBody = document.getElementById("alert-body");
    const alertUrl = document.getElementById("alert-url");

    alertContainer.hidden = true;
    alertBody.innerText = "";
    alertUrl.innerText = "";
}

async function sendRequest(url, data) {
    let response = null;
    if(data === undefined){
        response = await fetch(url);
    } else {
        response = await fetch(url, data);
    }

    if(response === null){
        console.log("Response should not be null. There is some error in the code");
    }

  if (!response.ok){
      const content = await response.json();
      const alertContainer = document.getElementById("alert-container");
      const alertBody = document.getElementById("alert-body");
      const alertUrl = document.getElementById("alert-url");

        alertBody.innerText = JSON.stringify(content["body"]);
        alertUrl.innerText = content["url"];
        alertContainer.hidden = false;

    return null;
  } else{
    return response;
  }
}