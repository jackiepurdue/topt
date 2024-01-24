$.ajaxSetup({
    beforeSend: function (xhr) {
        if (xhr.overrideMimeType) {
            xhr.overrideMimeType("application/json");
        }
    }
});


var nodeStyleTree =
    [

        {
            "selector": 'node',
            "style": {
                "label": "data(id)",
                'background-color': '#11479e'
            }
        },
        {
            "selector": 'edge',
            "style": {
                'width': 4,
                'target-arrow-shape': 'triangle',
                'line-color': '#9dbaea',
                'target-arrow-color': '#9dbaea',
                'curve-style': 'bezier'
            }
        }
    ];

function midpoint(x1, y1, x2, y2) {
    return [(x1 + x2) / 2, (y1 + y2) / 2];
}


function add_transfers(cy) {

    let sprEdges = cy.elements(".sprNode").map(function (sprEdge) {
        return sprEdge.id().split("_");
    });

    if (sprEdges.length > 0) {
        for (let i = 0; i < sprEdges.length; i++) {
            let node0 = cy.getElementById(sprEdges[i][0])
            let node1 = cy.getElementById(sprEdges[i][1])
            let sprNodePosition0 = node0.position();
            let sprNodePosition1 = node1.position();
            let edge_midpoint = midpoint(sprNodePosition0.x, sprNodePosition0.y, sprNodePosition1.x, sprNodePosition1.y)

            midNode = cy.getElementById(node0.id() + "_" + node1.id())
            midNode.json({
                position: {
                    x: edge_midpoint[0],
                    y: edge_midpoint[1]
                    //x:sprNodePosition0.x,
                    //y:sprNodePosition0.y
                }
            })
        }
    }
}


function add_transfers2(cy) {


    let sprEdges = cy.elements(".sourceNode").map(function (sprEdge) {
        return sprEdge.id().split("_");
    });

    if (sprEdges.length > 0) {
        for (let i = 0; i < sprEdges.length; i++) {
            let node0 = cy.getElementById(sprEdges[i][0])
            let node1 = cy.getElementById(sprEdges[i][1])
            let sprNodePosition0 = node0.position();
            let sprNodePosition1 = node1.position();
            let edge_midpoint = midpoint(sprNodePosition0.x, sprNodePosition0.y, sprNodePosition1.x, sprNodePosition1.y)

            midNode = cy.getElementById(node0.id() + "_" + node1.id())
            midNode.json({
                position: {
                    x: edge_midpoint[0],
                    y: edge_midpoint[1]
                    //x:sprNodePosition0.x,
                    //y:sprNodePosition0.y
                }
            })
        }
    }


    let sprEdges2 = cy.elements(".targetNode").map(function (sprEdge) {
        return sprEdge.id().split("_");
    });

    if (sprEdges2.length > 0) {
        for (let i = 0; i < sprEdges2.length; i++) {
            let node0 = cy.getElementById(sprEdges2[i][0])
            let node1 = cy.getElementById(sprEdges2[i][1])
            let node1id = JSON.stringify(node0.id())
            //let othernode = node1id.toString()
            let othernodeid = node1id.split("@")[0].substring(1)

            let nodea = cy.getElementById(othernodeid)
            let sprNodePosition = nodea.position();
            // let edge_midpoint = midpoint(sprNodePosition0.x, sprNodePosition0.y, sprNodePosition1.x, sprNodePosition1.y)
            //[firstPart, secondPart] = node0.id().split("_");
            midNode = cy.getElementById(node0.id())
            midNode.json({
                position: {
                    x: sprNodePosition.x,
                    y: sprNodePosition.y
                    //x:sprNodePosition0.x,
                    //y:sprNodePosition0.y
                }
            })
        }
    }
}

function restyle(cy) {
    cy.style().selector('.node').style({
        'height': 8,
        'width': 8,
        'color': '#E4860D'
    }).update();
    cy.style().selector('.leaf').style({
        'height': 16,
        'width': 16,

        'font-weight': 900,
        'background-color': '#E4860D',
        'color': '#000000'
    }).update();
    cy.style().selector('.internal').style({
        'label': ''
    }).update();
    cy.style().selector('.sprNode').style({
        'label': ''
    }).update();
    cy.style().selector('.spareSprNode').style({
        'label': ''
    }).update();
    cy.style().selector('.sprEdge').style({
        'curve-style': 'unbundled-bezier',
        'target-arrow-shape': 'triangle',
        'control-point-weights': '0.5 0.5',
        'line-color': '#E4860D',
        'line-style': 'dotted'
    }).update();

    cy.style().selector('.spareSprEdge').style({
        'curve-style': 'unbundled-bezier',
        'target-arrow-shape': 'triangle',
        'control-point-weights': '0.5 0.5',
        'line-color': '#E4860D',
        'line-style': 'dotted'
    }).update();
    cy.style().selector('.spareSprNode').style({
        'height': 5,
        'width': 5,
    }).update();

    cy.style().selector('.sprNode').style({
        'height': 5,
        'width': 5,
    }).update();
    cy.style().selector('.internal').style({
        'height': 5,
        'width': 5,
    }).update();
}

function makeTree(cy2) {
    // Get all nodes in the graph
    var nodes = cy2.nodes();


    const dfs = (cy, rootNode) => {
        // Initialize the stack with the root node and its depth
        const stack = [{node: rootNode, depth: 0}];
        const visited = new Set();

        while (stack.length > 0) {
            // Pop the next node and its depth from the stack
            const {node, depth} = stack.pop();

            // If the node has already been visited, skip it
            if (visited.has(node)) {
                continue;
            }

            // Mark the node as visited
            visited.add(node);

            // Do whatever processing you need to do on the node
            console.log(`Node ${node.id()} is at depth ${depth}`);
            node.data('depth', depth);

            // Add the child nodes to the stack with their depths incremented by 1
            node.outgoers().forEach((child) => {
                stack.push({node: child, depth: depth + 1});
            });
        }
    };

    dfs(cy2, nodes[0]);

// Start the BFS traversal


    // Define the distance between parent and child nodes
    var distance = 300;

    // Loop through each node in the graph
    nodes.forEach(function (node) {
        // Find the edges that connect the node to its parent
        nid = node.id()
        var edges = node.outgoers();
        depth = node.data('depth');
        // If the node has a parent
        if (edges.length == 2) {
            // Find the parent node
            // Set the x and y position of the node based on its parent-child relationship
            var x = node.position().x - distance / (depth * depth * 0.2 + 2);
            var y = node.position().y + distance / (depth * depth * 0.2 + 2);

            var lnode = edges[0].target()
            lnode.position({x: x, y: y});
        } else if (edges.length == 4) {

            var x = node.position().x - distance / (depth * depth * 0.2 + 2);
            var y = node.position().y + distance / (depth * depth * 0.2 + 2);

            var lnode = edges[0].target()
            lnode.position({x: x, y: y});

            x = node.position().x + distance / (depth * depth * 0.2 + 2);
            y = node.position().y + distance / (depth * depth * 0.2 + 2);

            var rnode = edges[2].target()
            rnode.position({x: x, y: y});
        }

    });


}


function findNode(id, currentNode) {
    var i, currentChild, result;

    // Check if the current node has the ID we are looking for in its "data" object
    if (currentNode.decision.data[id]) {
        return currentNode.decision.data[id];
    } else {
        // If not, check each child node recursively
        for (i = 0; i < currentNode.children.length; i += 1) {
            currentChild = currentNode.children[i];

            // Search in the current child
            result = findNode(id, currentChild);

            // Return the result if the node has been found
            if (result !== false) {
                return result;
            }
        }

        // The node has not been found and we have no more options
        return false;
    }
}


$.getJSON("http://localhost:8000/api/", function (data) {


    Swal.fire({
        //title: 'tree',
        html: "<div id='cy2'></div>",
        confirmButtonText: 'Cool',
        didOpen: function () {
            t = node["tree"]
            var cy = cytoscape({
                container: document.getElementById('cy2'),
                elements: t,
                style: nodeStyleTree,
                //layout: {name: 'breadthfirst'}
                //layout: {name: 'preset'} //this is in progress
                layout: {name: 'dagre'}
            });

            cy.fit();
            restyle(cy)

            console.log(node)
        },
        onClose: function () {
            // Remove the cytoscape instance and its container when the popup is closed
            //cy.destroy();
            $("#cy2").remove();
        }
    });
});


/*
$.getJSON("http://localhost:8000/api/", function (data) {
    new DataTree({
        json: data,
        container: "#tree",
        clickCallback: function (event, li, state) {
            // Do something when a node is clicked
            let id = event.attr('class');
            let preId = id.split("x")[0]

            if (preId == "tmid") {
                console.log("Node class:", id);
                node = findNode(id, data)

                Swal.fire({
                    //title: 'tree',
                    html: "<div id='cy2'></div>",
                    confirmButtonText: 'Cool',
                    didOpen: function() {
                        t = node["tree"]
                        var cy = cytoscape({
                            container: document.getElementById('cy2'),
                            elements: t,
                            style: nodeStyleTree,
                            //layout: {name: 'breadthfirst'}
                            //layout: {name: 'preset'} //this is in progress
                            layout: {name: 'dagre'}
                        });

                        cy.fit();
                        restyle(cy)

                        console.log(node)
                    },
                    onClose: function() {
                        // Remove the cytoscape instance and its container when the popup is closed
                        //cy.destroy();
                        $("#cy2").remove();
                    }
                });
            }
        }
    });
});*/

