
var BASE_MARKDOWN_PATH = 'KB';

function bindMarkdownClickHandler() {
    if (typeof network === 'undefined') {
        console.error('Network object not found');
        return;
    }

    network.on("click", function (params) {
        console.log('Node clicked:', params);
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];
            var markdownPath = BASE_MARKDOWN_PATH + '/' + encodeURI(nodeId);
            console.log('Loading content for node:', nodeId, 'from', markdownPath);

            fetch(markdownPath)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP error ' + response.status);
                    }
                    return response.text();
                })
                .then(content => {
                    document.getElementById('markdown-body').innerHTML = marked.parse(content);
                    var modal = new bootstrap.Modal(document.getElementById('markdownModal'));
                    modal.show();
                })
                .catch(error => {
                    console.error('Lỗi khi load nội dung:', error);
                    alert('Lỗi khi tải nội dung: ' + error.message);
                });
        }
    });
}

function disablePhysicsAfterStabilization() {
    if (typeof network === 'undefined') {
        return;
    }
    
    network.once('stabilizationIterationsDone', function() {
        network.setOptions({ physics: false });
        console.log('Graph stabilized and physics disabled');
    });
}

// Đảm bảo marked.js đã load
function waitForMarked(callback) {
    if (typeof marked !== 'undefined') {
        callback();
    } else {
        setTimeout(function() { waitForMarked(callback); }, 100);
    }
}

waitForMarked(function() {
    if (document.readyState === 'complete') {
        bindMarkdownClickHandler();
        disablePhysicsAfterStabilization();
    } else {
        window.addEventListener('load', function() {
            bindMarkdownClickHandler();
            disablePhysicsAfterStabilization();
        });
    }
});
