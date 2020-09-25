function get_timer(timestamp, id_display, durata){
    console.log("mostro qui->"+id_display)
    // Set the date we're counting down to
    //old _ new Date("Jan 5, 2021 15:37:25").getTime()
    var inizio = new Date(timestamp).getTime();
    var countDownDate = inizio + (parseInt(durata)*1000);
    
    console.log("ORA: " + inizio + " \n countdown: " + countDownDate)

    // Update the count down every 1 second
    var x = setInterval(function() {

        // Get today's date and time
        var now = new Date().getTime();

        // Find the distance between now and the count down date
        var distance = countDownDate - now;

        // Time calculations for days, hours, minutes and seconds
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Display the result in the element with id="demo"
        document.getElementById(id_display).innerHTML = days + "d " + hours + "h "
        + minutes + "m " + seconds + "s ";

        // If the count down is finished, write some text
        if (distance < 0) {
            clearInterval(x);
            document.getElementById(id_display).innerHTML = "Laboratorio Stoppato Automaticamente";
            new_num = parseInt($("#num_notifications").text()) + 1;
            $("#num_notifications").html(""+new_num+"");
            $("#num_notifications").css("display","inline");
        }
    }, 1000);
}