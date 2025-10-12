<div id="midbar">
    <div class="buttons">
    <button onclick="window.location.href='../'">Back</button>
    <button onclick="window.location.href = './mde/{{f.pretty_filename}}'">Edit</button>
    <button onclick="deleteFile('{{ f.absolute_path }}')">Delete</button>
</div>
<h5>{{f.pretty_filename}}</h5>
</div>
