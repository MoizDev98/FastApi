<div class="markdown-body">
	<script src="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js"></script>
    <script>
    localStorage.removeItem('smde_editor');
    </script>
	<textarea id="editor">
		{{!info}}
	</textarea>
	<script>
		var s = new SimpleMDE({
			element: document.getElementById("editor"),
			spellChecker: false,
			autosave: {
				enabled: true,
				unique_id: "editor",
			},
		});
	</script>
</div>
