<div class="markdown-body">
	<script src="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js"></script>
    <script>
    localStorage.removeItem('smde_demo2');
    </script>
	<textarea id="demo2">
		{{!info}}
	</textarea>
	<script>
		var s = new SimpleMDE({
			element: document.getElementById("demo2"),
			spellChecker: false,
			autosave: {
				enabled: true,
				unique_id: "demo2",
			},
		});
		s.clearAutosaveValue();
	</script>
</div>
