






CKEDITOR.replace('default', {
    allowedContent: true,
    filebrowserUploadUrl: '/ckeditor/upload/',
    filebrowserBrowseUrl: '/filer/browse/',
    filebrowserUploadMethod: 'form',
    extraPlugins: 'uploadimage,image2,justify,widget',
    toolbar: [
        ['Undo', 'Redo'],
        ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
        ['Link', 'Unlink', 'Anchor'],
        ['Image', 'UploadImage', 'Flash', 'Table', 'HorizontalRule', 'SpecialChar'],
        ['Format', 'FontSize', 'TextColor', 'BGColor', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
        ['NumberedList', 'BulletedList', 'Blockquote', 'Code', 'Source']
    ],
    height: 300,
});




