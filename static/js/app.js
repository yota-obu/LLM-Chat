document.getElementById("chat-form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    const preProfile = document.getElementById("pre_profile").value;
    const query = document.getElementById("query").value;

    const requestData = {
        pre_profile: preProfile,
        query: query
    };

    fetch("http://localhost:8080/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("エラーが発生しました: " + data.error);
        } else {
            const profile = data.profile;
            const answer = data.response;

            document.getElementById("response-text").textContent = "プロファイル: " + profile + "\n\n応答: " + answer;
            document.getElementById("response").style.display = "block";
        }
    })
    .catch(error => {
        alert("通信エラー: " + error.message);
    });
});
