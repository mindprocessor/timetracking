 function timelapse(given_datetime){
    //let current_datetime = Date.parse('<?php echo current_datetime(); ?>');
    let parse_datetime = moment(given_datetime);
    let current_datetime = moment(Date.now());
    let time_diff = current_datetime.diff(parse_datetime); //milliseconds

    let time_elapsed = moment.utc(time_diff).format('HH:mm:ss');
    return time_elapsed;
}



up.log.enable();
//up.protocol.config.csrfHeader = "X-CSRFToken";

up.on('up:fragment:loaded', (event) => {
    let response = event.response;
    let responseCode = event.response.status;
    console.log(response);
    if(responseCode !== 200){
        event.preventDefault();
        document.write(response.text);
    }
});


up.on('confirm:delete', function(event) {
    x = confirm('Are you sure you want to delete selected record?');
    if(x == true){
        return true;
    }else{
        event.preventDefault();
    }
});

/*
up.compiler('.data-tables', function(element) {
  new DataTable(element, {
    scrollX: true,
    //stateSave: true,
  });
});
*/

/**time counter for checking */
up.compiler('.checkin-record', function(){
    let checkin_datetime = $('#checkin-datetime').text();

    setInterval( () => {
        let curr = moment(Date.now()).format('YYYY-MM-DD HH:mm:ss');

        if(checkin_datetime !== ''){
            let time_elapsed = timelapse(checkin_datetime);
            $('.time-elapsed').html(time_elapsed);
        }

    }, 1000);
});

/**time counter for break */
up.compiler('.checkin-break-record', function(){
    let break_time_start = $('#break-time-start').text();

    setInterval( () => {
        let curr = moment(Date.now()).format('YYYY-MM-DD HH:mm:ss');
        
        if(break_time_start !== ''){
            let bk_time_elapsed = timelapse(break_time_start);
            $('.bk-time-elapsed').html(bk_time_elapsed);
        }

    }, 1000);

});
