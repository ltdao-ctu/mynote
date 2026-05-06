
function bindMarkdownClickHandler() {
    if (typeof network === 'undefined') {
        console.error('Network object not found');
        return;
    }

    network.on("click", function (params) {
        console.log('Node clicked:', params);
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];
            console.log('Loading content for node:', nodeId);
            
            // Load nội dung từ file JSON riêng
            fetch('markdown_contents.json')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP error ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Loaded data keys:', Object.keys(data));
                    var content = data[nodeId];
                    if (content) {
                        console.log('Found content for node:', nodeId);
                        document.getElementById('markdown-body').innerHTML = marked.parse(content);
                        var modal = new bootstrap.Modal(document.getElementById('markdownModal'));
                        modal.show();
                    } else {
                        console.error('Không tìm thấy nội dung cho node:', nodeId, 'Available keys:', Object.keys(data));
                        alert('Không tìm thấy nội dung cho file này');
                    }
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
