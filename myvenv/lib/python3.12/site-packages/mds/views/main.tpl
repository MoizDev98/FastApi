<html>
<head>
	<title>{{!title}}</title>
	<link rel="stylesheet" href="./static/styles.css">
	<link rel="stylesheet" href="./static/sam.css">
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
</head>
<body>
% include(nav)
<div class="container">
% include(bar)
% include(content)
</div>
<script src="./static/search.js"></script>
</body>
</html>
