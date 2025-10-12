function newNote() {
	var newNoteName = prompt("Note name:", "enter text here...");

	if (newNoteName == null || newNoteName == "") {
	  alert("No note name entered");
	} else {
	  $.ajax({
		async: false,
		type : "POST",
		url : '/mde/new',
		dataType: "json",
		data: JSON.stringify({"note_name": newNoteName}),
		contentType: 'application/json;charset=UTF-8',
		success: function (data) {
			console.log(data);
				alert("File saved successfully")
			},
			error: function(data) {
				alert("Error saving file");
				console.log(data);
			},
		});	  
	} 
}

function saveFile(absolute_path) {
    $.ajax({
	async: false,
	type : "POST",
	url : '/mde/save',
	dataType: "json",
	data: JSON.stringify({"saved_value": s.value(), "absolute_path": absolute_path}),
	contentType: 'application/json;charset=UTF-8',
	success: function (data) {
		console.log(data);
			alert("File saved successfully")
		},
		error: function(data) {
			alert("Error saving file");
			console.log(data);
		},
	});
}

function deleteFile(absolute_path) {
	if (confirm("Are you sure you want to delete this file")) {
    $.ajax({
		async: false,
		type : "POST",
		url : '/mde/delete',
		dataType: "json",
		data: JSON.stringify({"absolute_path": absolute_path}),
		contentType: 'application/json;charset=UTF-8',
		success: function (data) {
				window.location.replace("/");
			},
			error: function(data) {
				alert("Error deleting file");
				console.log(data);
			},
		});		
	} else {
		alert("File not deleted")
	}

}



