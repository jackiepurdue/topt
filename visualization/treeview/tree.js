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
                'target-arrow-shape': 'none',
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


function add_transfers_type_2(cy) {


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


function move_links_to_parent_level(cy) {
  cy.elements('.link').forEach(linkNode => {
    const sourceNode = linkNode.source();
    const targetNode = linkNode.target();
    const parent = targetNode.parent();
    const parentPos = parent.position();
    const parentHeight = parent.height();
    const targetPos = targetNode.position();
    const targetHeight = targetNode.height();

    // Set the y coordinate of the link node to the y coordinate of its parent
    const linkNodeY = parentPos.y + parentHeight / 2;
    linkNode.position({ x: targetPos.x, y: linkNodeY });

    // Adjust the length of the edge so that it doesn't overlap with the parent node
    const dy = (targetPos.y - targetHeight / 2) - linkNodeY;
    const edgeLength = Math.abs(dy) * 2;
    linkNode.style('curve-style', 'unbundled-bezier');
    linkNode.style('control-point-distance', edgeLength / 2);
    linkNode.style('control-point-weight', 0.5);
  });
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
    cy.style().selector('.targetNode').style({
        'label': ''
    }).update();
    cy.style().selector('.sourceNode').style({
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
    cy.style().selector('.link').style({
        'height': 1,
        'width': 1,

        'font-weight': 900,
        'background-color': '#33cc33',
        'color': '#000000',
        'label': ''
    }).update();

    cy.style().selector('.sprNode').style({
        'height': 5,
        'width': 5,
    }).update();
    cy.style().selector('.internal').style({
        'height': 5,
        'width': 5,

    }).update();
    cy.style().selector('.inserted').style({
        'height': 12,
        'width': 12,
        'label': '',
        'background-color': '#ff66cc'
    }).update();
    cy.style().selector('.expanding').style({
        'height': 16,
        'width': 16,

        'font-weight': 900,
        'background-color': '#33cc33',
        'color': '#000000',
        'label': ''
    }).update();
    cy.style().selector('.expanded').style({
        'height': 24,
        'width': 24,
        'font-weight': 900,
        'background-color': '#33ff33',
        'color': '#000000',
        'label': ''
    }).update();
    cy.style().selector('.reversing').style({
        'height': 16,
        'width': 16,

        'font-weight': 900,
        'background-color': '#ff66cc',
        'color': '#000000',
        'label': ''
    }).update();

    cy.style().selector('.finish').style({
        'height': 24,
        'width': 24,

        'font-weight': 900,
        'background-color': '#006600',
        'color': '#000000',
        'label': ''
    }).update();

    cy.style().selector('.reversed').style({
        'height': 12,
        'width': 12,

        'font-weight': 900,
        'background-color': '#aD66ff',
        'color': '#000000',
        'label': ''
    }).update();

    cy.style().selector('.start').style({
        'height': 12,
        'width': 12,

        'font-weight': 900,
        'background-color': '#ffff66',
        'color': '#000000',
        'label': ''
    }).update();

    cy.style().selector('.matched').style({
        'height': 12,
        'width': 12,
        'font-weight': 900,
        'background-color': '#99ff33',
        'color': '#000000',
        'label': ''
    }).update();

    cy.style().selector('.compared').style({
        'height': 12,
        'width': 12,

        'font-weight': 900,
        'background-color': '#6699ff',
        'color': '#000000',
        'label': ''
    }).update();

    cy.style().selector('.invalid').style({
        'height': 12,
        'width': 12,

        'font-weight': 900,
        'background-color': '#ff0000',
        'color': '#000000',
        'label': ''
    }).update();
}


function concatenateCytoscapeGraphs(graphs) {
  let nodes = [];
  let edges = [];

  for (let i = 0; i < graphs.length; i++) {
    const graph = graphs[i];

    // Add nodes
    for (let j = 0; j < graph.nodes.length; j++) {
      const node = JSON.parse(JSON.stringify(graph.nodes[j]));
      node.data.id = node.data.id+"_"+i
      nodes.push(node);
    }

    // Add edges
    for (let j = 0; j < graph.edges.length; j++) {
      const edge = JSON.parse(JSON.stringify(graph.edges[j]));
      edge.data.source = edge.data.source+"_"+i;
      edge.data.target = edge.data.target+"_"+i;
      //const source = edge.data().source + "_" + i;
      //const target = edge.data().target + "_" + i;
      edges.push(edge);
    }
  }

  // Update edge source and target IDs to account for added nodes

  concatenatedGraph = { nodes, edges };

  return concatenatedGraph;
}


function run_cytoscape(data) {
    var cy1 = cytoscape({
        container: document.getElementById('cy1'),
        elements: data["decision_nodes"],
        style: nodeStyleTree,
        layout: {
            name: 'dagre',
            rankSep: 20, // adjust rank separation to control distance between ranks
            nodeSep: 20, // adjust node separation to control distance between nodes within a rank
            // Other layout options (if needed)
            // rankDir: 'LR', // set direction of the DAG (default is TB)
            //spacingFactor: 1.5, // adjust spacing between nodes (default is 1.75)
            // edgeWeight: function(edge) { return edge.data('weight'); }, // use edge weight for edge length (default is 1)
        },
    });


    cy1.fit();
    restyle(cy1)

    cy1.on('tap', 'node', function (event) {

        var nodeId = event.target.id();
        console.log('Clicked node with ID:', nodeId);
        console.log(data["data"][nodeId])

        dataForNode = data["data"][nodeId]
        state = dataForNode["state"]

        if (state == "expanding" || state == "expanded" || state == "reversing" || state == "reversed") {
            var cy2 = cytoscape({
                container: document.getElementById('cy2'),
                elements: dataForNode["data"][0]["tree"],
                style: nodeStyleTree,
                //layout: {name: 'breadthfirst'}
                //layout: {name: 'preset'} //this is in progress
                layout: {
                    name: 'dagre',
                    rankDir: 'TB',
                    ranker: 'longest-path',
                    maxLen: 3
                    //rankSep: 20, // adjust rank separation to control distance between ranks
                    //nodeSep: 20, //
                }
            });

            cy2.fit();
            restyle(cy2)
            add_transfers(cy2)
            move_links_to_parent_level(cy2)

        } else if (state == "compared") {
            console.log("wfwefwefew")
            var cy2 = cytoscape({
                container: document.getElementById('cy2'),
                elements: concatenateCytoscapeGraphs([dataForNode["data"][1]["tree"], dataForNode["data"][0]["tree"]]),
                style: nodeStyleTree,
                //layout: {name: 'breadthfirst'}
                //layout: {name: 'preset'} //this is in progress
                layout: {
                    name: 'dagre',

                    rankDir: 'TB',
                    ranker: 'longest-path',
                    maxLen: 3
                    //rankSep: 20, // adjust rank separation to control distance between ranks
                    //nodeSep: 20,

                }
            });

            cy2.fit();
            restyle(cy2)
            //add_transfers_type_2(cy2)
            //move_links_to_parent_level(cy2)

            const forest_trees = [];

            for (let i = 1; i < dataForNode["data"].length; i++) {
              const forest_tree = dataForNode["data"][i]["tree"];
              forest_trees.push(forest_tree);
            }

            concatdata = concatenateCytoscapeGraphs(forest_trees.slice(1,forest_trees.length))

                      var cy3 = cytoscape({
                container: document.getElementById('cy3'),
                elements: concatdata,
                style: nodeStyleTree,
                //layout: {name: 'breadthfirst'}
                //layout: {name: 'preset'} //this is in progress
                layout: {
                    name: 'dagre',
                    rankDir: 'TB',
                    ranker: 'longest-path',
                    maxLen: 3
                    //rankSep: 20, // adjust rank separation to control distance between ranks
                    //nodeSep: 20,

                }
            });

            cy3.fit();
            restyle(cy3)
            //add_transfers_type_2(cy3)
            //move_links_to_parent_level(cy3)

        }
        else if (state == "finish") {
            var cy2 = cytoscape({
                container: document.getElementById('cy2'),
                elements: dataForNode["data"][0]["tree"],
                style: nodeStyleTree,
                //layout: {name: 'breadthfirst'}
                //layout: {name: 'preset'} //this is in progress
                layout: {
                    name: 'dagre',
                    rankDir: 'TB',
                    ranker: 'longest-path',
                    maxLen: 3
                    //rankSep: 20, // adjust rank separation to control distance between ranks
                    //nodeSep: 20,

                }
            });

            cy2.fit();
            restyle(cy2)
            add_transfers_type_2(cy2)
            //move_links_to_parent_level(cy2)

                      var cy3 = cytoscape({
                container: document.getElementById('cy3'),
                elements: dataForNode["data"][0]["tree"],
                style: nodeStyleTree,
                //layout: {name: 'breadthfirst'}
                //layout: {name: 'preset'} //this is in progress
                layout: {
                    name: 'dagre',
                    rankDir: 'TB',
                    ranker: 'longest-path',
                    maxLen: 3
                    //rankSep: 20, // adjust rank separation to control distance between ranks
                    //nodeSep: 20,

                }
            });

            cy3.fit();
            restyle(cy3)
            add_transfers_type_2(cy3)
            //move_links_to_parent_level(cy3)

        }


    });
}

$(document).ready(function () {
    var currentIndex = 0
    var DATA;

    $.getJSON("http://localhost:8000/api/", function (d) {
        DATA = d;
        data = d[0]
        all_data = data["data"]
        decison_nodes = data["decision_nodes"]

        run_cytoscape(data);
    });

    $('.prev').on('click', () => {
        // Hide the current slide
        // Move to the previous slide
        currentIndex--;
        if (currentIndex < 0) {
            currentIndex = Object.keys(DATA).length - 1;
        }
        Swal.fire({
            position: 'top-end',
            //icon: 'success',
            title: (currentIndex + 1) + ' of ' + Object.keys(DATA).length,
            showConfirmButton: false,
            timer: 1500,
            background: 'none',
            backdrop: false,
            showClass: {
                backdrop: 'swal2-noanimation', // disable backdrop animation
                popup: '',                     // disable popup animation
                icon: ''                       // disable icon animation
            },
            hideClass: {
                popup: '',                     // disable popup fade-out animation
            },
        })

        run_cytoscape(DATA[currentIndex])
    });

    $('.next').on('click', () => {
        // Hide the current slide
        // Move to the next slide
        currentIndex++;
        if (currentIndex >= Object.keys(DATA).length) {
            currentIndex = 0;
        }

        Swal.fire({
            position: 'top-end',
            //icon: 'success',
            title: (currentIndex + 1) + ' of ' + Object.keys(DATA).length,
            showConfirmButton: false,
            timer: 1500,
            background: 'none',
            backdrop: false,
            showClass: {
                backdrop: 'swal2-noanimation', // disable backdrop animation
                popup: '',                     // disable popup animation
                icon: ''                       // disable icon animation
            },
            hideClass: {
                popup: '',                     // disable popup fade-out animation
            },
        })

        run_cytoscape(DATA[currentIndex])
    });
});