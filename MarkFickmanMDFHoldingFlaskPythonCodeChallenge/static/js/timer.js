//create count up timer in javascript

/*
Count up timer based on basing the activation time for each
unique call in the active call log

By: Mark Fickman
*/

var startTimer = function(item) {

    //initialize startDateTime variable and holders for start and timer
    console.log("item: ", item)
    var startDateTime = new Date(item.startTime)
    console.log("startDateTime", startDateTime)
    var startStamp = startDateTime.getTime();
    var newDate = new Date();
    var newStamp = newDate.getTime();
    var timer;

    //create function to update date time show
    //utilize necessary math functions
    function updateClock() {
        newDate = new Date();
        newStamp = newDate.getTime();
        var diff = Math.round((newStamp-startStamp)/1000);

        var d = Math.floor(diff/(24*60*60));
        diff = diff-(d*24*60*60);
        var h = Math.floor(diff/(60*60));
        diff = diff-(h*60*60);
        var m = Math.floor(diff/(60));
        diff = diff-(m*60);
        var s = diff;

        document.getElementById(item.id).innerHTML = d+" day(s), "+h+" hour(s), "+m+" minute(s), "+s+" second(s) active";
    }

    timer = setInterval(updateClock, 1000);

}

