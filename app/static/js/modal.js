window.onload = function() {
    var modal = document.getElementById('myModal');

    // Get the button that opens the modal
    var btn = document.getElementById("myBtn");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on the button, open the modal
    btn.onclick = function() {
        modal.style.display = "inherit";

    };

    var options =
    {
        imageBox: '.imageBox',
        thumbBox: '.thumbBox',
        spinner: '.spinner',
        imgSrc: 'avatar.png'
    };
    var cropper;
    document.querySelector('#file').addEventListener('change', function(){
        var reader = new FileReader();
        reader.onload = function(e) {
            options.imgSrc = e.target.result;
            cropper = new cropbox(options);
        };
        reader.readAsDataURL(this.files[0]);
        this.files = [];
    });
    document.querySelector('#btnCrop').addEventListener('click', function(){
        var img = cropper.getDataURL();

        document.querySelector('.cropped').innerHTML = '<img src="'+img+'">';
        document.getElementById("photo-src").innerHTML = img;

    });
    document.querySelector('#btnZoomIn').addEventListener('click', function(){
        cropper.zoomIn();
    });
    document.querySelector('#btnZoomOut').addEventListener('click', function(){
        cropper.zoomOut();
    });

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    };

    var btnCrop = document.getElementById("btnCrop");
    btnCrop.onclick = function(){
        modal.style.display="none";
    };

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
};