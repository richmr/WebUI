$('#pickFile_button').on('click', function() {
    $('#pickFile').trigger('click');
});

$('#pickFile').change(function() {
  filelist = $('#pickFile').prop("files");
  thefilename = filelist[0].name;
  $('#fileinfo-text').append("<br>" + thefilename);
});
