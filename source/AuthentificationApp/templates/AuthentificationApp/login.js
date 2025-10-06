$(function() {

    $("form#loginForm").submit(function(event) {
            Loader.start();
            var url = "{% url 'AuthentificationApp:login_ajax' %}";
            var formData = new FormData($(this)[0]);
            $.post({
                url: url,
                data: formData,
                processData: false,
                contentType: false
            }, function(data) {
                if (data.status) {
                    console.log(data)
                    if (data.is_new) {
                        localStorage.setItem("employe_id", data.id)
                        $("#modal-new-user").modal("show");
                        if (data.secret) {
                            $("#secret-phrase .input-group").hide();
                            $("#secret-phrase .input-group input").attr("type", "hidden");
                            $("#secret-phrase label").text(data.phrase_secrete);
                        }else{
                            $("#secret-phrase .input-group").show();
                            $("#secret-phrase .input-group input").attr("type", "text");
                            $("#secret-phrase label").text("Définissez une question secrète");
                        }
                        
                    } else {
                        window.location.href = "{% url 'MainApp:dashboard' %}";
                    }
                } else {
                    Alerter.error('Erreur !', data.message);
                }
                Loader.stop();
            });
            return false;
        });



        $("form#formNewUser").submit(function(event) {
            Loader.start();
            var url = "{% url 'AuthentificationApp:first_user' %}";
            var formData = new FormData($(this)[0]);
            formData.append("employe_id", localStorage.getItem("employe_id"))
            $.post({
                url: url,
                data: formData,
                processData: false,
                contentType: false
            }, function(data) {
                if (data.status) {
                    window.location.href = "{% url 'MainApp:dashboard' %}";
                } else {
                    Alerter.error('Erreur !', data.message);
                }
            });
            return false;
        });
    })