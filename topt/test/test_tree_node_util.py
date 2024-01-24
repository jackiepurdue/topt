from functools import partial

import pytest

import topt.topt as topt
from topt.topt import TreeNode, Move, NodeData, Record, Status


def count_internal_nodes(tree: TreeNode) -> int:
    if len(tree.children) == 0:
        return 0
    else:
        return 1 + count_internal_nodes(tree.children[0]) + count_internal_nodes(tree.children[1])


def test_min_leaves_greater_than_max_leaves():
    with pytest.raises(ValueError):
        topt.create_random_binary_tree(10, 5, ["A", "B", "C"])


def test_min_labels_greater_than_max_leaves():
    with pytest.raises(ValueError):
        topt.create_random_binary_tree(4, 4, ["A", "B", "C", "D", "E"])


def test_num_leaves():
    tree = topt.create_random_binary_tree(3, 3, ["A", "B", "C"])
    assert len(topt.get_leaf_nodes(tree)) == 3


def test_root_label():
    tree = topt.create_random_binary_tree(3, 3, ["A", "B", "C"])
    assert tree.data.label == ""


def test_num_internal_nodes():
    tree = topt.create_random_binary_tree(3, 3, ["A", "B", "C"])
    assert count_internal_nodes(tree) == 2


def test_get_node_move_leaf():
    tree = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    move = Move({"a"}, {"d"})
    node_move = topt.get_node_label_move(tree, move)
    assert node_move == move


def test_get_node_move():
    tree = topt.label_tree(topt.generate_tree_node_from_newick("(((a,b),(c,d)),(e,f));"), 0)
    move = Move({"a", "b"}, {"d", "c"})
    node_move = topt.get_node_label_move(tree, move)
    assert node_move == Move({"2"}, {"5"})


def test_get_up_edges_chained_to_root():
    # Tree with chain of nodes having a single child
    t6 = TreeNode(NodeData("F"), [])
    t5 = TreeNode(NodeData("E"), [t6])
    t4 = TreeNode(NodeData("D"), [t5])
    t3 = TreeNode(NodeData("C"), [t4])
    t2 = TreeNode(NodeData("B"), [t3])
    t1 = TreeNode(NodeData("A"), [t2])
    uped = topt.get_up_edges(t1, t6)
    assert uped == [t2, t3, t4, t5, t6]


def test_get_up_edges_chained_to_inner():
    # Tree with chain of nodes having a single child
    h = TreeNode(NodeData("H"), [])
    g = TreeNode(NodeData("G"), [])
    f = TreeNode(NodeData("F"), [])
    e = TreeNode(NodeData("E"), [f])
    d = TreeNode(NodeData("D"), [e,h])
    c = TreeNode(NodeData("C"), [d])
    b = TreeNode(NodeData("B"), [g])
    a = TreeNode(NodeData("A"), [b, c])

    print(topt.generate_newick(a))
    uped = topt.get_up_edges(a, g)
    assert uped == [b,g]
    uped = topt.get_up_edges(a, f)
    assert uped == [e, f]

def test_get_up_edges_situation_just_like_get_parent():
    # Tree with chain of nodes having a single child
    h = TreeNode(NodeData("H"), [])
    g = TreeNode(NodeData("G"), [])
    f = TreeNode(NodeData("F"), [])
    e = TreeNode(NodeData("E"), [f])
    d = TreeNode(NodeData("D"), [e,h])
    c = TreeNode(NodeData("C"), [d])
    b = TreeNode(NodeData("B"), [g])
    a = TreeNode(NodeData("A"), [b, c])

    print(topt.convert_to_ete(a))
    uped = topt.get_up_edges(a, h)
    assert uped == [h]


def test_get_all_moves():
    tree = topt.label_tree(topt.generate_tree_node_from_newick("(B,((A,(C,D))),E);"), 0)
    move = Move({"5"},{"B"})
    print(topt.convert_to_ete(tree))
    new_tree, _ = topt.subtree_delete_and_regraft_single_labeled_move_tupled(tree, move)
    print(topt.convert_to_ete(new_tree))
    move2 = Move({"E"}, {"D"})
    new_tree2, _ = topt.subtree_delete_and_regraft_single_labeled_move_tupled(new_tree, move2)
    print(topt.convert_to_ete(new_tree2))
    move3 = Move({"C"}, {"B"})
    new_tree3, _ = topt.subtree_delete_and_regraft_single_labeled_move_tupled(new_tree2, move3)
    print(topt.convert_to_ete(new_tree3))
    move4 = Move({"E"}, {"B"})
    new_tree4, _ = topt.subtree_delete_and_regraft_single_labeled_move_tupled(new_tree3, move4)
    print(topt.convert_to_ete(new_tree4))

    all_moves = topt.get_possible_moves_from_move(new_tree4, Move({"A"}, {"D"}))
    assert len(all_moves) == 9

def test_get_possible_moves_from_move():
    # create a tree
    root = TreeNode(NodeData("A"), [
        TreeNode(NodeData("B"), [
            TreeNode(NodeData("G"), [])
        ]),
        TreeNode(NodeData("C"), [
            TreeNode(NodeData("D"), [
                TreeNode(NodeData("E"), [
                    TreeNode(NodeData("F"), [])
                ]),
                TreeNode(NodeData("H"), [])
            ])
        ])
    ])

    print(topt.convert_to_ete(root))
    print(topt.generate_newick(root))
    # test when source and target are at the same level
    move = Move(source={'F'}, target={'G'})
    actual_moves = topt.get_possible_moves_from_move(root, move)
    assert len(actual_moves) == 4

    expected_moves = [
        Move(source={'F'}, target={'G'}),
        Move(source={'F'}, target={'B'}),
        Move(source={'E'}, target={'G'}),
        Move(source={'E'}, target={'B'})
    ]

    for expected_move in expected_moves:
        assert expected_move.source in [m.source for m in actual_moves]
        assert expected_move.target in [m.target for m in actual_moves]


def test_get_possible_moves_from_move():
    # create a tree
    root = TreeNode(NodeData("A"), [
        TreeNode(NodeData("B"), [
            TreeNode(NodeData("G"), [])
        ]),
        TreeNode(NodeData("C"), [
            TreeNode(NodeData("D"), [
                TreeNode(NodeData("E"), [
                    TreeNode(NodeData("F"), [])
                ]),
                TreeNode(NodeData("H"), [])
            ])
        ])
    ])

    print(topt.convert_to_ete(root))
    print(topt.generate_newick(root))
    # test when source and target are at the same level
    move = Move(source={'E'}, target={'B'})
    actual_moves = topt.get_possible_moves_from_move(root, move)
    assert len(actual_moves) == 1

    expected_moves = [
        Move(source={'E'}, target={'B'}),
    ]

    for expected_move in expected_moves:
        assert expected_move.source in [m.source for m in actual_moves]
        assert expected_move.target in [m.target for m in actual_moves]

def test_get_possible_moves_from_move():
    # create a tree
    root = TreeNode(NodeData("A"), [
        TreeNode(NodeData("B"), [
            TreeNode(NodeData("G"), [])
        ]),
        TreeNode(NodeData("C"), [
            TreeNode(NodeData("D"), [
                TreeNode(NodeData("E"), [
                    TreeNode(NodeData("F"), [])
                ]),
                TreeNode(NodeData("H"), [])
            ])
        ])
    ])

    print(topt.convert_to_ete(root))
    print(topt.generate_newick(root))
    # test when source and target are at the same level
    move = Move(source={'F'}, target={'B'})
    actual_moves = topt.get_possible_moves_from_move(root, move)
    assert len(actual_moves) == 2

    expected_moves = [
        Move(source={'F'}, target={'B'}),
        Move(source={'E'}, target={'B'}),
    ]

    for expected_move in expected_moves:
        assert expected_move.source in [m.source for m in actual_moves]
        assert expected_move.target in [m.target for m in actual_moves]



def test_randbin():
    #topt.create_random_binary_tree()
    pass

def _make():
    #ref_tree = topt.generate_tree_node_from_newick("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));")
    ref_tree = topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));")
    listoftup = topt.create_tree_pairs_with_minimum_spr_distance_with_subset_of_this_reference_tree(ref_tree, 4, 100)
    for tup in listoftup:
        print(tup[0] + " " + tup[1])

def make0():
    #ref_tree = topt.generate_tree_node_from_newick("(((a,b),c),(d,((e,(((f,g),(h,(i,j))),k)),((l,(m,n)),(o,p)))));")
    ref_tree = topt.generate_tree_node_from_newick("((f,(e,(((c,b),a),d))),g);")
    listoftup = topt.create_tree_pairs_with_minimum_spr_distance_with_subset_of_this_reference_tree(ref_tree, 1, 100)
    for tup in listoftup:
        print(tup[0] + " " + tup[1])

def make2():
    ref_tree = topt.generate_tree_node_from_newick("(((((((ace,(act,add)),(ado,age)),(((aid,(aim,(air,ale))),all),(amp,(and,ant)))),(any,ape)),((((apt,arc),((are,ark),(arm,art))),((((ash,ask),(ass,ate)),((awe,axe),aye)),(((((bad,bag),bam),(ban,bar)),(((bat,(((bay,(bed,bee)),((beg,((bet,bib),(bid,(big,bin)))),(bit,boa))),((((bob,bog),(boo,bot)),box),boy))),((((bra,bub),(bud,bug)),((bum,bun),bus)),but)),((((buy,(bye,cab)),(cad,(cam,can))),((cap,car),cat)),((((caw,(cob,cod)),cog),col),con)))),((cop,((cot,cow),(coy,cry))),(cub,(cue,cup)))))),(((cut,dad),(((dam,dan),(dap,day)),(den,des))),((((((((dew,did),dig),(dim,din)),dip),(doc,dog)),((don,(dot,(dry,dub))),(dud,(due,(dug,duh))))),(dye,(ear,(eat,ebb)))),((((((eel,egg),(ego,(eke,elf))),(elk,ell)),(((elm,end),(eon,era)),((ere,((erg,((ern,err),eta)),(eve,(ewe,eye)))),fad))),(((fag,fan),(far,fas)),((((fat,fax),(((fed,fee),fen),(few,(fib,fig)))),fin),(fir,((fit,((fix,flu),fly)),fob))))),((foe,fog),(for,fox))))))),((((((fry,fum),((fun,fur),gab)),(gad,gag)),((gap,gas),gay)),(gee,(gel,gem))),((((get,(gig,gin)),(god,(goo,got))),(((((gum,gun),(gut,guy)),gym),((had,(hag,(hah,(ham,has)))),(hat,(hay,hem)))),((((hen,her),((hew,hex),hey)),(hid,(him,hip))),(his,hit)))),hob))),(hoc,(hog,(hop,hot))));")
    #ref_tree = topt.generate_tree_node_from_newick("(a,((b,c),(((d,e),f),((g,h),i))));")
    listoftup = topt.create_tree_pairs_with_minimum_spr_distance_with_subset_of_this_reference_tree(ref_tree, 60, 1)
    with open('./files/tree_pairs_long_labels_SPR30_N1.csv', 'w') as f:
        for tup in listoftup:
            print(tup[0] + " " + tup[1])
            f.writelines(str(tup[0]) + " " + str(tup[1])+"\n")

def test_random_binary_tree(tnt=None):
    for i in range(0, 10):
        l = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p"]
        binary_tree = topt.create_random_binary_tree(4, 16, l)
        assert isinstance(binary_tree, TreeNode)

def test_random_binary_tree_large(tnt=None):
    for i in range(0, 1):
        l = ["ace", "act", "add", "ado", "age", "aid", "aim", "air", "ale", "all", "amp", "and", "ant", "any", "ape",
             "apt", "arc", "are", "ark", "arm", "art", "ash", "ask", "ass", "ate", "awe", "axe", "aye", "bad", "bag",
             "bam", "ban", "bar", "bat", "bay", "bed", "bee", "beg", "bet", "bib", "bid", "big", "bin", "bit", "boa",
             "bob", "bog", "boo", "bot", "box", "boy", "bra", "bub", "bud", "bug", "bum", "bun", "bus", "but", "buy",
             "bye", "cab", "cad", "cam", "can", "cap", "car", "cat", "caw", "cob", "cod", "cog", "col", "con", "cop",
             "cot", "cow", "coy", "cry", "cub", "cue", "cup", "cut", "dad", "dam", "dan", "dap", "day", "den", "des",
             "dew", "did", "dig", "dim", "din", "dip", "doc", "dog", "don", "dot", "dry", "dub", "dud", "due", "dug",
             "duh", "dye", "ear", "eat", "ebb", "eel", "egg", "ego", "eke", "elf", "elk", "ell", "elm", "end", "eon",
             "era", "ere", "erg", "ern", "err", "eta", "eve", "ewe", "eye", "fad", "fag", "fan", "far", "fas", "fat",
             "fax", "fed", "fee", "fen", "few", "fib", "fig", "fin", "fir", "fit", "fix", "flu", "fly", "fob", "foe",
             "fog", "for", "fox", "fry", "fum", "fun", "fur", "gab", "gad", "gag", "gap", "gas", "gay", "gee", "gel",
             "gem", "get", "gig", "gin", "god", "goo", "got", "gum", "gun", "gut", "guy", "gym", "had", "hag", "hah",
             "ham", "has", "hat", "hay", "hem", "hen", "her", "hew", "hex", "hey", "hid", "him", "hip", "his", "hit",
             "hob", "hoc", "hog", "hop", "hot", "how", "hub", "hue", "hug", "hum", "hut", "ice", "icy", "ill", "imp",
             "ink", "inn", "ion", "ire", "irk", "its", "ivy", "jab", "jag", "jam", "jar", "jaw", "jay", "jet", "jig",
             "job", "jog", "jot", "joy", "jug", "jut", "keg", "ken", "key", "kid", "kin", "kip", "kit", "lab", "lad",
             "lag", "lam", "lap", "law", "lax", "lay", "lea", "led", "lee", "leg", "let", "lid", "lie", "lip", "lit",
             "lob", "log", "loo", "lop", "lot", "low", "lox", "lug", "lum", "lux", "lye", "mac", "mad", "maf", "mag",
             "man", "map", "mar", "mat", "maw", "max", "may", "men", "met", "mew", "mid", "mil", "min", "mit", "mix",
             "mob", "mod", "mom", "moo", "mop", "mow", "mud", "mug", "mum", "nab", "nag", "nap", "nay", "nee", "net",
             "new", "nib", "nil", "nip", "nit", "nix", "nob", "nod", "non", "nor", "not", "now", "nun", "nus", "nut",
             "oak", "oar", "oat", "odd", "off", "oft", "ohm", "oil", "old", "ole", "one", "ooh", "opt", "orb", "ore",
             "our", "out", "ova", "owl", "own", "pad", "pal", "pan", "pap", "par", "pat", "paw", "pay", "pea", "peg",
             "pen", "pep", "per", "pet", "pew", "phi", "pic", "pie", "pig", "pin", "pip", "pit", "ply", "pod", "pop",
             "pot", "pow", "pro", "pry", "pub", "pug", "pun", "pup", "pus", "put", "qua", "rad", "rag", "ram", "ran",
             "rap", "rat", "raw", "ray", "red", "ref", "rem", "rep", "ret", "rib", "rid", "rig", "rim", "rip", "rob",
             "rod", "roe", "rot", "row", "rub", "rue", "rug", "rum", "run", "rut", "rye", "sea", "see", "set", "sew",
             "sex", "she", "shy", "sib", "sic", "sim", "sin", "sip", "sir", "sis", "sit", "six", "ski", "sky", "sly",
             "sob", "sod", "sol", "son", "sop", "sot", "sow", "soy", "spa", "spy", "sub", "sue", "sum", "sun", "sup",
             "tab", "tad", "tag", "tan", "tap", "tar", "tat", "tau", "tax", "tea", "ted", "tee", "ten", "the", "tho",
             "thy", "tic", "tie", "til", "tin", "tip", "tis", "tit", "toe", "tog", "tom", "ton", "too", "top", "tor",
             "tot", "tow", "toy", "try", "tub", "tug", "tum", "tun", "tup", "tut", "tux", "twa", "two", "tye", "ugh",
             "ump", "uns", "upo", "ups", "urn", "use", "uta", "ute", "uts", "vac", "van", "vat", "vaw", "vee", "vet",
             "vex", "via", "vie", "vim", "vow", "vox", "wad", "wag", "wan", "wap", "war", "was", "wax", "way", "web",
             "wed", "wee", "wen", "wet", "wha", "who", "why", "wig", "win", "wit", "wiz", "woe", "wok", "won", "woo",
             "wow", "wry", "wud", "wye", "wyn", "xis", "yah", "yak", "yam", "yap", "yar", "yaw", "yay", "yea", "yen",
             "yep", "yes", "yet", "yew", "yid", "yin", "yip", "yod", "yok", "yom", "yon", "you", "yow", "yuk", "yum",
             "yup", "zag", "zap", "zed", "zee", "zek", "zig", "zin", "zip", "zit", "zoo"]
        binary_tree = topt.create_random_binary_tree(200, 200, l)
        print(topt.generate_newick(binary_tree))
        assert isinstance(binary_tree, TreeNode)

def test_random_binary_tree_file(tnt=None):
    with open('./files/1_3_long_labels.csv', 'w') as f:
        for i in range(0, 3):
            l = ["ace", "act", "add", "ado", "age", "aid", "aim", "air", "ale", "all", "amp", "and", "ant", "any",
                 "ape", "apt", "arc", "are", "ark", "arm", "art", "ash", "ask", "ass", "ate", "awe", "axe", "aye",
                 "bad", "bag", "bam", "ban", "bar", "bat", "bay", "bed", "bee", "beg", "bet", "bib", "bid", "big",
                 "bin", "bit", "boa", "bob", "bog", "boo", "bot", "box", "boy", "bra", "bub", "bud", "bug", "bum",
                 "bun", "bus", "but", "buy", "bye", "cab", "cad", "cam", "can", "cap", "car", "cat", "caw", "cob",
                 "cod", "cog", "col", "con", "cop", "cot", "cow", "coy", "cry", "cub", "cue", "cup", "cut", "dad",
                 "dam", "dan", "dap", "day", "den", "des", "dew", "did", "dig", "dim", "din", "dip", "doc", "dog",
                 "don", "dot", "dry", "dub", "dud", "due", "dug", "duh", "dye", "ear", "eat", "ebb", "eel", "egg",
                 "ego", "eke", "elf", "elk", "ell", "elm", "end", "eon", "era", "ere", "erg", "ern", "err", "eta",
                 "eve", "ewe", "eye", "fad", "fag", "fan", "far", "fas", "fat", "fax", "fed", "fee", "fen", "few",
                 "fib", "fig", "fin", "fir", "fit", "fix", "flu", "fly", "fob", "foe", "fog", "for", "fox", "fry",
                 "fum", "fun", "fur", "gab", "gad", "gag", "gap", "gas", "gay", "gee", "gel", "gem", "get", "gig",
                 "gin", "god", "goo", "got", "gum", "gun", "gut", "guy", "gym", "had", "hag", "hah", "ham", "has",
                 "hat", "hay", "hem", "hen", "her", "hew", "hex", "hey", "hid", "him", "hip", "his", "hit", "hob",
                 "hoc", "hog", "hop", "hot", "how", "hub", "hue", "hug", "hum", "hut", "ice", "icy", "ill", "imp",
                 "ink", "inn", "ion", "ire", "irk", "its", "ivy", "jab", "jag", "jam", "jar", "jaw", "jay", "jet",
                 "jig", "job", "jog", "jot", "joy", "jug", "jut", "keg", "ken", "key", "kid", "kin", "kip", "kit",
                 "lab", "lad", "lag", "lam", "lap", "law", "lax", "lay", "lea", "led", "lee", "leg", "let", "lid",
                 "lie", "lip", "lit", "lob", "log", "loo", "lop", "lot", "low", "lox", "lug", "lum", "lux", "lye",
                 "mac", "mad", "maf", "mag", "man", "map", "mar", "mat", "maw", "max", "may", "men", "met", "mew",
                 "mid", "mil", "min", "mit", "mix", "mob", "mod", "mom", "moo", "mop", "mow", "mud", "mug", "mum",
                 "nab", "nag", "nap", "nay", "nee", "net", "new", "nib", "nil", "nip", "nit", "nix", "nob", "nod",
                 "non", "nor", "not", "now", "nun", "nus", "nut", "oak", "oar", "oat", "odd", "off", "oft", "ohm",
                 "oil", "old", "ole", "one", "ooh", "opt", "orb", "ore", "our", "out", "ova", "owl", "own", "pad",
                 "pal", "pan", "pap", "par", "pat", "paw", "pay", "pea", "peg", "pen", "pep", "per", "pet", "pew",
                 "phi", "pic", "pie", "pig", "pin", "pip", "pit", "ply", "pod", "pop", "pot", "pow", "pro", "pry",
                 "pub", "pug", "pun", "pup", "pus", "put", "qua", "rad", "rag", "ram", "ran", "rap", "rat", "raw",
                 "ray", "red", "ref", "rem", "rep", "ret", "rib", "rid", "rig", "rim", "rip", "rob", "rod", "roe",
                 "rot", "row", "rub", "rue", "rug", "rum", "run", "rut", "rye", "sea", "see", "set", "sew", "sex",
                 "she", "shy", "sib", "sic", "sim", "sin", "sip", "sir", "sis", "sit", "six", "ski", "sky", "sly",
                 "sob", "sod", "sol", "son", "sop", "sot", "sow", "soy", "spa", "spy", "sub", "sue", "sum", "sun",
                 "sup", "tab", "tad", "tag", "tan", "tap", "tar", "tat", "tau", "tax", "tea", "ted", "tee", "ten",
                 "the", "tho", "thy", "tic", "tie", "til", "tin", "tip", "tis", "tit", "toe", "tog", "tom", "ton",
                 "too", "top", "tor", "tot", "tow", "toy", "try", "tub", "tug", "tum", "tun", "tup", "tut", "tux",
                 "twa", "two", "tye", "ugh", "ump", "uns", "upo", "ups", "urn", "use", "uta", "ute", "uts", "vac",
                 "van", "vat", "vaw", "vee", "vet", "vex", "via", "vie", "vim", "vow", "vox", "wad", "wag", "wan",
                 "wap", "war", "was", "wax", "way", "web", "wed", "wee", "wen", "wet", "wha", "who", "why", "wig",
                 "win", "wit", "wiz", "woe", "wok", "won", "woo", "wow", "wry", "wud", "wye", "wyn", "xis", "yah",
                 "yak", "yam", "yap", "yar", "yaw", "yay", "yea", "yen", "yep", "yes", "yet", "yew", "yid", "yin",
                 "yip", "yod", "yok", "yom", "yon", "you", "yow", "yuk", "yum", "yup", "zag", "zap", "zed", "zee",
                 "zek", "zig", "zin", "zip", "zit", "zoo"]
            binary_tree = topt.create_random_binary_tree(80, 100, l)
            f.write(str(binary_tree) + '\n')

