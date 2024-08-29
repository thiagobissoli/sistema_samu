$(document).ready(function(){
    $(".btn-toggle").click(function(event){
        event.preventDefault();

        const button = $(this);
        const recordId = button.data('record-id');
        const checkpointName = button.data('checkpoint-name');

        fetch("/patio/toggle-checkpoint", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                record_id: recordId,
                checkpoint_name: checkpointName
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success") {
                const newValue = data.new_value;
                if(newValue === 0) {
                    button.removeClass('btn-danger btn-success').addClass('btn-secondary');
                } else if(newValue === 1) {
                    button.removeClass('btn-secondary btn-success').addClass('btn-danger');
                } else {
                    button.removeClass('btn-secondary btn-danger').addClass('btn-success');
                }
            } else {
                alert("Erro ao alternar o checkpoint!");
            }
        })
        .catch(error => {
            console.error("Erro na requisição:", error);
            alert("Erro na requisição!");
        });
    });

    $(".btn-toggle-prev").click(function(event){
        event.preventDefault();

        const button = $(this);
        const recordId = button.data('record-id');
        const checkpointName = button.data('checkpoint-name');

        fetch("/patio/toggle-previsao", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                record_id: recordId,
                checkpoint_name: checkpointName
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === "success") {
                const newValue = data.new_value;
                if(newValue === 0) {
                    button.removeClass('btn-danger').addClass('btn-secondary');
                } else {
                    button.removeClass('btn-secondary').addClass('btn-danger');
                }
            } else {
                alert("Erro ao alternar o checkpoint!");
            }
        })
        .catch(error => {
            console.error("Erro na requisição:", error);
            alert("Erro na requisição!");
        });
    });
});
