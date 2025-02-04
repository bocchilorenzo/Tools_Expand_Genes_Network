import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib as mpl
import networkx as nx
import numpy as np
from operator import itemgetter
from matplotlib_venn import venn3, venn2
import lib.components_graph as comp
import lib.utilities_expansion as utex
import lib.utilities as ut
import lib.venn as vennD
import re
import random

#Draw general graph
def drawGraph(type_gene, net, namefile, pearson, autoSaveImg, list_Genes, range_frel, comprimeNode, typePrint, typeDB):
    #range to divide type of edges
    step1_range = round((range_frel/3)+1-range_frel, 2)
    step2_range = round((range_frel/3*2)+1-range_frel, 2)
    #set name of window and change parameters of save image
    namefiles = namefile.split('/')
    plt.figure(namefiles[2])
    mpl.rcParams['savefig.dpi'] = 700
    mpl.rcParams['savefig.directory'] = namefiles[0]+'/'+namefiles[1]
    #convert name genes to number
    idNode = {}
    i = 1
    edges = []
    newPearson = []
    for k in net:
        if k[0] not in idNode:
            idNode[k[0]] = i
            i += 1
        if k[1] not in idNode:
            idNode[k[1]] = i
            i += 1
    for k in net:
        edges.append((idNode[k[0]], idNode[k[1]], k[2]))
    for k in pearson:
        try:
            newPearson.append((idNode[k[0]], idNode[k[1]], k[2]))
        except:
            pass #edge of complete graph not in core

    #code to define colors for each isoform. Only for Human genes
    dict_isoColor = {}
    if type_gene == 'H' and not comprimeNode:
        if list(idNode.keys())[0][0] == '@':
            for k in list_Genes:
                if '@' in k:
                    nameG = re.search(r'@\w*', k)
                    if nameG and nameG.group() not in idNode.keys():
                        edges.append((i, i, 1))
                        newPearson.append((i, i, 1))
                        idNode[nameG.group()] = i
                        i += 1
        else:
            for k in list_Genes:
                if k not in idNode.keys():
                    edges.append((i, i, 1))
                    newPearson.append((i, i, 1))
                    idNode[k] = i
                    i += 1

        #create color for each isoform
        isoform_done = {}
        for g in edges:
            #print((list(idNode.keys())[list(idNode.values()).index(g[0])]))
            if '@' in (list(idNode.keys())[list(idNode.values()).index(g[0])]):
                isoform = re.search(r'@\w*', (list(idNode.keys())[list(idNode.values()).index(g[0])]))
                if isoform:
                    if isoform.group() not in isoform_done.keys():
                        dict_isoColor[g[0]] = "#" + "%06x" % random.randint(0, 0xFFFFFF)
                        isoform_done[(isoform.group())] = g[0]
                    else:
                        dict_isoColor[g[0]] = dict_isoColor[isoform_done[isoform.group()]]
            if '@' in (list(idNode.keys())[list(idNode.values()).index(g[1])]):
                isoform = re.search(r'@\w*', (list(idNode.keys())[list(idNode.values()).index(g[1])]))
                if isoform:
                    if isoform.group() not in isoform_done.keys():
                        dict_isoColor[g[1]] = "#" + "%06x" % random.randint(0, 0xFFFFFF)
                        isoform_done[(isoform.group())] = g[1]
                    else:
                        dict_isoColor[g[1]] = dict_isoColor[isoform_done[isoform.group()]]
    else:
        for k in list_Genes:
            if k not in idNode.keys():
                edges.append((i, i, 1))
                newPearson.append((i, i, 1))
                idNode[k] = i
                i += 1

    #order id based on name gene
    oldidNode = idNode.copy()
    tmpKeys = sorted(idNode.keys())
    for k in tmpKeys:
        idNode[k] = tmpKeys.index(k)+1
    i = 0
    while i < len(edges):
        tmp = edges[i]
        edges[i] = (list(oldidNode.keys())[list(oldidNode.values()).index(tmp[0])].split('@')[1], list(oldidNode.keys())[list(oldidNode.values()).index(tmp[1])].split('@')[1], tmp[2])
        i += 1
    i = 0
    while i < len(newPearson):
        tmp = newPearson[i]
        newPearson[i] = (list(oldidNode.keys())[list(oldidNode.values()).index(tmp[0])].split('@')[1], list(oldidNode.keys())[list(oldidNode.values()).index(tmp[1])].split('@')[1], tmp[2])
        i += 1

    G = nx.Graph()
    for e in edges:
        G.add_edge(e[0], e[1], weight=e[2])

    #print the connected components of the complete graph
    if len(list_Genes) > 0 and not typePrint:
        subgraphs = sorted(list(G.subgraph(c) for c in nx.connected_components(G)), key=len, reverse=True)
        f = open(namefile+'_connected_components.txt', 'w')
        i = 0
        while i < len(subgraphs):
            s = subgraphs[i]
            if len(s.nodes()) > 1:
                f.write('Node subgraph '+str(i+1)+':\n')
                lNodes = []
                for n in s.nodes():
                    lNodes.append(n)
                f.write(str(lNodes)+'\n')
            i += 1
        f.close()
        print('Create: '+namefile+'_connected_components.txt', flush=True)

    ePos = [(u, v) for (u, v, p) in newPearson if p >= 0]
    eNeg = [(u, v) for (u, v, p) in newPearson if p < 0]

    estrongPos = [(u, v) for (u, v, d) in G.edges(data=True) if float(d['weight']) > step2_range and ((u, v) in ePos or (v, u) in ePos)]
    estrongNeg = [(u, v) for (u, v, d) in G.edges(data=True) if float(d['weight']) > step2_range and ((u, v) in eNeg or (v, u) in eNeg)]
    emediumPos = [(u, v) for (u, v, d) in G.edges(data=True) if float(d['weight']) <= step2_range and d['weight'] > step1_range and ((u, v) in ePos or (v, u) in ePos)]
    emediumNeg = [(u, v) for (u, v, d) in G.edges(data=True) if float(d['weight']) <= step2_range and d['weight'] > step1_range and ((u, v) in eNeg or (v, u) in eNeg)]
    eweakPos = [(u, v) for (u, v, d) in G.edges(data=True) if float(d['weight']) <= step1_range and ((u, v) in ePos or (v, u) in ePos)]
    eweakNeg = [(u, v) for (u, v, d) in G.edges(data=True) if float(d['weight']) <= step1_range and ((u, v) in eNeg or (v, u) in eNeg)]
    # positions for all nodes
    pos = comp.layout_many_components(G, component_layout_func=nx.layout.circular_layout)
    if typePrint:
        pos = comp.layout_many_components(G, component_layout_func=nx.layout.spring_layout)
    # nodes
    n_size = 150
    f_size = 8
    e_size = 2
    if len(idNode.keys()) > 100:
        n_size = 7
        f_size = 1
        e_size = 0.2
    elif len(idNode.keys()) >= 50 and len(idNode.keys()) < 100:
        n_size = 15
        f_size = 2
        e_size = 0.5
    elif len(idNode.keys()) >= 30 and len(idNode.keys()) < 50:
        n_size = 50
        f_size = 4
        e_size = 1
    elif len(idNode.keys()) >= 15 and len(idNode.keys()) < 30:
        n_size = 150
        f_size = 8
        e_size = 1.5
    
    vector_isoColor = []
    for node in G.nodes():
        if 'SNO' in node:
            vector_isoColor.append('#80FF80')
        else:
            vector_isoColor.append('#88cafc')
    nx.draw_networkx_nodes(G, pos, node_size=n_size, node_color=vector_isoColor)
    # edges
    nx.draw_networkx_edges(G, pos, edgelist=estrongPos, width=e_size, edge_color='black')
    nx.draw_networkx_edges(G, pos, edgelist=emediumPos, width=e_size/2, edge_color='black', style='dashed')
    nx.draw_networkx_edges(G, pos, edgelist=eweakPos, width=e_size/2, edge_color='black', style='dotted')
    nx.draw_networkx_edges(G, pos, edgelist=estrongNeg, width=e_size, edge_color='red')
    nx.draw_networkx_edges(G, pos, edgelist=emediumNeg, width=e_size/2, edge_color='red', style='dashed')
    nx.draw_networkx_edges(G, pos, edgelist=eweakNeg, width=e_size/2, edge_color='red', style='dotted')
    # labels
    nx.draw_networkx_labels(G, pos, font_size=f_size, font_family='sans-serif', font_color='#0000FF')
    plt.axis('off')

    #title
    # if 'Core' in namefile:
    #     plt.title('Core of Network')
    # else:
    #     plt.title('Complete Graph')
    #legend
    black_line = mlines.Line2D([], [], linewidth=2, color='black', label='frel > '+str(step2_range))
    blue_line = mlines.Line2D([], [], linewidth=1, color='black', label=str(step1_range)+' < frel <= '+str(step2_range), linestyle='dashed')
    red_line = mlines.Line2D([], [], linewidth=1, color='black', label='frel <= '+str(step1_range), linestyle='dotted')
    if comprimeNode:
        black_line = mlines.Line2D([], [], linewidth=2, color='black', label='average frel > '+str(step2_range))
        blue_line = mlines.Line2D([], [], linewidth=1, color='black', label=str(step1_range)+' < average frel <= '+str(step2_range), linestyle='dashed')
        red_line = mlines.Line2D([], [], linewidth=1, color='black', label='average frel <= '+str(step1_range), linestyle='dotted')
    pos_line = mlines.Line2D([], [], linewidth=1, color='black', label='Pearson corr. >= 0')
    neg_line = mlines.Line2D([], [], linewidth=1, color='red', label='Pearson corr. < 0')
    idName = mlines.Line2D([], [], label='ID --> NAME', visible=False)
    if len(eNeg) > 0:
        #textLegend = [black_line, blue_line, red_line, pos_line, neg_line, idName]
        textLegend = [black_line, blue_line, red_line, pos_line, neg_line] #todel
    else:
        #textLegend = [black_line, blue_line, red_line, idName]
        textLegend = [black_line, blue_line, red_line] #todel

    #Write legend ID-->GENE
    nameGenes = idNode.keys()
    dictStrToWrite = {}
    #Print legend for human
    f = open('import_doc/anno-hsf5.csv', 'r')
    text = f.readlines()
    listLineName = {}
    i = 1
    while i < len(text):
        tmpLine = text[i].split(',')
        if '@'+tmpLine[5][1:-1] in nameGenes:
            listLineName['@'+tmpLine[5][1:-1]] = ','.join([str(elem) for elem in tmpLine[1:]])
        i += 1
    fileOut = namefile.split('graph')[0]+'graph_legend_ID_NAME.csv'
    print('LEGEND IN: \''+fileOut+'\'')
    f = open(fileOut, 'w')
    f.write('ID,NODE,association_with_transcript,entrezgene_id,hgnc_id,uniprot_id,gene_name,description,type\n')
    tmpList = {}
    for k in nameGenes:
        tmpList[idNode[k]] = k
    for k in sorted(tmpList.keys()):
        try:
            f.write(str(k)+','+tmpList[k]+','+listLineName[tmpList[k]])
        except:
            f.write(str(k)+','+tmpList[k]+'\n')

    plt.legend(handles=textLegend, fontsize = 'xx-small').set_draggable(True)
    #autoSave PNG or show
    if autoSaveImg:
        namefile = namefile.replace("<", "_")
        namefile = namefile.replace(">", "_")
        plt.savefig(namefile+'.png')
        print('Create: \''+namefile+'.png\'', flush=True)
    else:
        plt.show()
    #Clean graph and pyplot
    G.clear()
    plt.clf()
    plt.close()

#Draw graph of expansion LGN
def printCommonGraph(listCommonGenes, pearsonComplete, range_frel, nameDir, autoSaveImg, listBioNameUpdate):
    #range to divide type of edges
    step1_range = round((range_frel/3)+1-range_frel, 2)
    step2_range = round((range_frel/3*2)+1-range_frel, 2)

    for l in listCommonGenes:
        #nameFile
        nameF = utex.buildNamefile(l)
        namefile = nameDir+str(listCommonGenes.index(l))+'/graphGenes'
        #set name of window and change parameters of save image
        plt.figure('graph')
        mpl.rcParams['savefig.directory'] = nameDir+nameF
        mpl.rcParams['savefig.dpi'] = 700
        #build edges of graph
        net = utex.buildEdges(l)
        pearson = pearsonComplete[listCommonGenes.index(l)]
        #convert name genes to number
        idNode = {}
        i = 1
        edges = []
        newPearson = []
        for k in net:
            if k[0] not in idNode:
                idNode[k[0]] = i
                i += 1
            if k[1] not in idNode:
                idNode[k[1]] = i
                i += 1
        for k in net:
            edges.append((idNode[k[0]], idNode[k[1]], k[2]))
        for k in pearson:
            try:
                newPearson.append((idNode[k[0]], idNode[k[1]], k[2]))
            except:
                pass #edge of complete graph not in core

        #Set color of nodes. Genes of LGN -> RED, associated genes -> BLUE
        dict_isoColor = {}
        isoform_done = {}
        for g in edges:
            #print((list(idNode.keys())[list(idNode.values()).index(g[0])]))
            if (list(idNode.keys())[list(idNode.values()).index(g[0])]) in l[0] and (list(idNode.keys())[list(idNode.values()).index(g[0])]) not in isoform_done.keys():
                dict_isoColor[g[0]] = "#FF3232"
                isoform_done[(list(idNode.keys())[list(idNode.values()).index(g[0])])] = g[0]
            elif (list(idNode.keys())[list(idNode.values()).index(g[0])]) not in isoform_done.keys():
                dict_isoColor[g[0]] = '#48B3FF'
                isoform_done[(list(idNode.keys())[list(idNode.values()).index(g[0])])] = g[0]
            if (list(idNode.keys())[list(idNode.values()).index(g[1])]) in l[0] and (list(idNode.keys())[list(idNode.values()).index(g[1])]) not in isoform_done.keys():
                dict_isoColor[g[1]] = "#FF3232"
                isoform_done[(list(idNode.keys())[list(idNode.values()).index(g[1])])] = g[1]
            elif (list(idNode.keys())[list(idNode.values()).index(g[1])]) not in isoform_done.keys():
                dict_isoColor[g[1]] = '#48B3FF'
                isoform_done[(list(idNode.keys())[list(idNode.values()).index(g[1])])] = g[1]

        #add edges to Graph
        G = nx.Graph()
        for e in edges:
            G.add_edge(e[0], e[1], weight=e[2])

        #divide edges by weight
        ePos = [(u, v) for (u, v, p) in newPearson if p >= 0]
        eNeg = [(u, v) for (u, v, p) in newPearson if p < 0]
        estrongPos = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > step2_range and ((u, v) in ePos or (v, u) in ePos)]
        estrongNeg = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > step2_range and ((u, v) in eNeg or (v, u) in eNeg)]
        emediumPos = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= step2_range and d['weight'] > step1_range and ((u, v) in ePos or (v, u) in ePos)]
        emediumNeg = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= step2_range and d['weight'] > step1_range and ((u, v) in eNeg or (v, u) in eNeg)]
        eweakPos = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= step1_range and ((u, v) in ePos or (v, u) in ePos)]
        eweakNeg = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= step1_range and ((u, v) in eNeg or (v, u) in eNeg)]
        pos = comp.layout_many_components(G, component_layout_func=nx.layout.spring_layout)

        # size of nodes, text and edges
        n_size = 150
        f_size = 8
        e_size = 2
        if len(idNode.keys()) > 100:
            n_size = 7
            f_size = 1
            e_size = 0.2
        elif len(idNode.keys()) >= 50 and len(idNode.keys()) < 100:
            n_size = 15
            f_size = 2
            e_size = 0.5
        elif len(idNode.keys()) >= 30 and len(idNode.keys()) < 50:
            n_size = 50
            f_size = 4
            e_size = 1
        elif len(idNode.keys()) >= 15 and len(idNode.keys()) < 30:
            n_size = 100
            f_size = 6
            e_size = 1.5

        #draw nodes
        vector_isoColor = []
        if len(dict_isoColor) > 0:
            for node in G.nodes():
                vector_isoColor.append(dict_isoColor[node])
        nx.draw_networkx_nodes(G, pos, node_size=n_size, node_color=vector_isoColor)
        vector_isoColor = []
        if len(dict_isoColor) > 0:
            for node in G.nodes():
                vector_isoColor.append(dict_isoColor[node])
        nx.draw_networkx_nodes(G, pos, node_size=n_size, node_color=vector_isoColor)
        # edges
        nx.draw_networkx_edges(G, pos, edgelist=estrongPos, width=e_size, edge_color='black')
        nx.draw_networkx_edges(G, pos, edgelist=emediumPos, width=e_size/2, edge_color='black', style='dashed')
        nx.draw_networkx_edges(G, pos, edgelist=eweakPos, width=e_size/2, edge_color='black', style='dotted')
        nx.draw_networkx_edges(G, pos, edgelist=estrongNeg, width=e_size, edge_color='red')
        nx.draw_networkx_edges(G, pos, edgelist=emediumNeg, width=e_size/2, edge_color='red', style='dashed')
        nx.draw_networkx_edges(G, pos, edgelist=eweakNeg, width=e_size/2, edge_color='red', style='dotted')
        # labels
        nx.draw_networkx_labels(G, pos, font_size=f_size, font_family='sans-serif')

        plt.axis('off')
        #plt.title("Graph LGN with related genes")
        #legend
        black_line = mlines.Line2D([], [], linewidth=2, color='black', label='frel > '+str(step2_range))
        blue_line = mlines.Line2D([], [], linewidth=1, color='black', label=str(step1_range)+' < frel <= '+str(step2_range), linestyle='dashed')
        red_line = mlines.Line2D([], [], linewidth=1, color='black', label='frel <= '+str(step1_range), linestyle='dotted')
        pos_line = mlines.Line2D([], [], linewidth=1, color='black', label='Pearson corr. >= 0')
        neg_line = mlines.Line2D([], [], linewidth=1, color='red', label='Pearson corr. < 0')
        if len(eNeg) > 0:
            textLegend = [black_line, blue_line, red_line, pos_line, neg_line]
        else:
            textLegend = [black_line, blue_line, red_line]
        circleLGN = mlines.Line2D(range(1), range(1), color="white", marker='o', markerfacecolor="#FF3232", label='Genes in LGN')
        circleNewNodes = mlines.Line2D(range(1), range(1), color="white", marker='o', markerfacecolor='#48B3FF', label='Discovered genes')
        textLegend.append(circleLGN)
        textLegend.append(circleNewNodes)
        #Write legend ID-->GENE
        nameGenes = idNode.keys()
        dictStrToWrite = {}
        #Read information of Vitis genes
            # f = open('import_doc/NewAnnotVitisnet3.csv', 'r')
            # text = f.readlines()
            # listLineName = []
            # i = 1
            # while i < len(text):
            #     listLineName.append(text[i].split(','))
            #     i += 1
            # for k in nameGenes:
            #     listBR = (list(listBioNameUpdate.keys())[list(listBioNameUpdate.values()).index(k)]).split('<BR>')
            #     for elem in listBR:
            #         try:
            #             if elem in [u[0].upper() for u in listLineName]:
            #                 index = [u[0].upper() for u in listLineName].index(elem)
            #                 u = listLineName[index]
            #                 dictStrToWrite[elem] = str(u[0])+','+str(u[1])+','+str(u[2])+','+str(u[3])+','+str(u[4])+','+str(u[5])
            #         except:
            #             pass
            # fileOut = namefile.split('graph')[0]+'graph_legend_ID_NAME.csv'
            # print('LEGEND IN: \''+fileOut+'\'')
            # f = open(fileOut, 'w')
            # f.write('ID in graph,'+text[0].split(',')[0]+','+text[0].split(',')[1]+','+text[0].split(',')[2]+','+text[0].split(',')[3]+','+text[0].split(',')[4]+','+text[0].split(',')[5])
            # for k in nameGenes:
            #     listBR = (list(listBioNameUpdate.keys())[list(listBioNameUpdate.values()).index(k)]).split('<BR>')
            #     for elem in listBR:
            #         try:
            #             f.write(str(idNode[k])+','+dictStrToWrite[elem])
            #         except:
            #             pass
            # f.close()
        #Print legend for human
        f = open('import_doc/anno-hsf5.csv', 'r')
        text = f.readlines()
        listLineName = {}
        i = 1
        while i < len(text):
            tmpLine = text[i].split(',')
            listGene = [u for u in nameGenes if '@' not in u]+[u.split('@')[1] for u in nameGenes if '@' in u]
            if tmpLine[5][1:-1] in listGene:
                listLineName[tmpLine[5][1:-1]] = ','.join([str(elem) for elem in tmpLine[1:]])
            i += 1
        fileOut = namefile.split('graph')[0]+'graph_legend_ID_NAME.csv'
        print('LEGEND IN: \''+fileOut+'\'')
        f = open(fileOut, 'w')
        f.write('ID,NODE,association_with_transcript,entrezgene_id,hgnc_id,uniprot_id,gene_name,description,type\n')
        tmpList = {}
        for k in nameGenes:
            tmpList[idNode[k]] = k
        for k in sorted(tmpList.keys()):
            try:
                if '@' not in tmpList[k]:
                    f.write(str(k)+','+tmpList[k]+','+listLineName[tmpList[k]])
                else:
                    f.write(str(k)+','+tmpList[k]+','+listLineName[tmpList[k].split('@')[1]])
            except:
                f.write(str(k)+','+tmpList[k]+'\n')

        #textLegend.append(mlines.Line2D([], [], label='in \''+(fileOut.split('/'))[-1]+'\'', visible=False))
        plt.legend(handles=textLegend, fontsize = 'xx-small').set_draggable(True)
        #autoSave PNG or show
        if autoSaveImg:
            namefile = namefile.replace("<", "_")
            namefile = namefile.replace(">", "_")
            plt.savefig(namefile+'.png')
            print('Create: \'graphGenes.png\'', flush=True)
        else:
            plt.show()
        #Clean graph and pyplot
        G.clear()
        plt.clf()
        plt.close()

#Draw Venn Diagram of common genes
def printVenn(listForVenn, couples, nameDir):
    for k in listForVenn:
        listKey = sorted([u for u in k.keys()], key=len)
        nameF = ''
        for g in sorted([u for u in listKey if len(u.split(',')) == 1]):
            if nameF == '':
                nameF = g.split('\'')[1]
            else:
                nameF += '_'+g.split('\'')[1]
        #Draw venn diagram with 2 sets
        if len([elem.split('\'')[1] for elem in list(k.keys()) if len(elem.split('\''))==3]) == 2:
            elemSubSets = (len(k[str(listKey[0])]), len(k[str(listKey[1])]), int(len(k[str(listKey[2])])/2))
            v = venn2(subsets = elemSubSets, set_labels = ((re.findall(r'\w+', str(listKey[0])))[0], (re.findall(r'\w+', str(listKey[1])))[0]))
            nameUnifyGenes = (re.findall(r'\w+', str(listKey[0])))[0] +'_'+ (re.findall(r'\w+', str(listKey[1])))[0]
            nameF = nameF.replace("<", "_")
            nameF = nameF.replace(">", "_")
            nameUnifyGenes = nameUnifyGenes.replace("<", "_")
            nameUnifyGenes = nameUnifyGenes.replace(">", "_")
            plt.savefig(nameDir+str(listForVenn.index(k))+'/venn.png')
            print('Create: \''+str(listForVenn.index(k))+'/venn.png\'')
        #Draw venn diagram with 3 sets
        if len([elem.split('\'')[1] for elem in list(k.keys()) if len(elem.split('\''))==3]) == 3:
            elemSubSets = ('',)
            if len(listKey) == 7:
                listKey = sorted(listKey[:3])+sorted(listKey[3:-1], key=itemgetter(0,1))+[listKey[-1]]
                #(A,B,AB,C,AC,BC,ABC)
                elemSubSets = (len(k[str(listKey[0])]), len(k[str(listKey[1])]), int(len(k[str(listKey[3])])/2), len(k[str(listKey[2])]), int(len(k[str(listKey[4])])/2), int(len(k[str(listKey[5])])/2), int(len(k[str(listKey[6])])/3))
                v = venn3(subsets = elemSubSets, set_labels = ((re.findall(r'\w+', str(listKey[0])))[0], (re.findall(r'\w+', str(listKey[1])))[0], (re.findall(r'\w+', str(listKey[2])))[0]))
            else:
                pass
                #TODO: find solution if there isn't some element in listKey
            nameUnifyGenes = (re.findall(r'\w+', str(listKey[0])))[0] +'_'+ (re.findall(r'\w+', str(listKey[1])))[0] +'_'+ (re.findall(r'\w+', str(listKey[2])))[0]
            nameF = nameF.replace("<", "_")
            nameF = nameF.replace(">", "_")
            nameUnifyGenes = nameUnifyGenes.replace("<", "_")
            nameUnifyGenes = nameUnifyGenes.replace(">", "_")
            plt.savefig(nameDir+str(listForVenn.index(k))+'/venn.png')
            print('Create: \''+str(listForVenn.index(k))+'/venn.png\'')
        #Draw Venn diagram with 4 sets
        if len([elem.split('\'')[1] for elem in list(k.keys()) if len(elem.split('\''))==3]) == 4:
            #made all possible combination of genes
            listKey = sorted([str([elem]) for elem in couples[listForVenn.index(k)]])
            listKeyL = sorted([[elem] for elem in couples[listForVenn.index(k)]])
            listKey.append(str([listKeyL[0][0],listKeyL[1][0],listKeyL[2][0],listKeyL[3][0]]))
            i = 0
            j = 1
            z = 2
            while i < 4:
                tmp = listKeyL[i][0]
                while j < 4:
                    listKey.append(str([tmp,listKeyL[j][0]]))
                    while z < 4:
                        listKey.append(str([tmp,listKeyL[j][0],listKeyL[z][0]]))
                        z+=1
                    j+=1
                    z=j+1
                i+=1
                j=i+1
                z=j+1
            listKey = sorted(listKey, key=len)
            keyAndNumber = [(key,len(k[key])) for key in sorted(k.keys(), key=len)]
            completeKeyNumber = {}
            for key in listKey:
                if key in [elem[0] for elem in keyAndNumber]:
                    completeKeyNumber[key] = keyAndNumber[[elem[0] for elem in keyAndNumber].index(key)][1]
                else:
                    completeKeyNumber[key] = 0
            #print(completeKeyNumber)
            dictLabels = {
                '0001': completeKeyNumber[listKey[0]],
                '0010': completeKeyNumber[listKey[1]],
                '0011': int(completeKeyNumber[listKey[4]]/2),
                '0100': completeKeyNumber[listKey[2]],
                '0101': int(completeKeyNumber[listKey[5]]/2),
                '0110': int(completeKeyNumber[listKey[7]]/2),
                '0111': int(completeKeyNumber[listKey[10]]/3),
                '1000': completeKeyNumber[listKey[3]],
                '1001': int(completeKeyNumber[listKey[6]]/2),
                '1010': int(completeKeyNumber[listKey[8]]/2),
                '1011': int(completeKeyNumber[listKey[11]]/3),
                '1100': int(completeKeyNumber[listKey[9]]/2),
                '1101': int(completeKeyNumber[listKey[12]]/3),
                '1110': int(completeKeyNumber[listKey[13]]/3),
                '1111': int(completeKeyNumber[listKey[14]]/4),
            }
            v = vennD.venn4(dictLabels, names=[listKeyL[3][0],listKeyL[2][0],listKeyL[1][0],listKeyL[0][0]])
            nameUnifyGenes = str(listKeyL[0][0]) +'_'+ str(listKeyL[1][0]) +'_'+ str(listKeyL[2][0]) +'_'+ str(listKeyL[3][0])
            nameF = nameF.replace("<", "_")
            nameF = nameF.replace(">", "_")
            nameUnifyGenes = nameUnifyGenes.replace("<", "_")
            nameUnifyGenes = nameUnifyGenes.replace(">", "_")
            plt.savefig(nameDir+str(listForVenn.index(k))+'/venn.png')
            print('Create: \''+str(listForVenn.index(k))+'/venn.png\'')
        #Draw Venn diagram with 5 sets
        if len([elem.split('\'')[1] for elem in list(k.keys()) if len(elem.split('\''))==3]) == 5:
            #made all possible combination of genes
            listKey = sorted([str([elem]) for elem in couples[listForVenn.index(k)]])
            listKeyL = sorted([[elem] for elem in couples[listForVenn.index(k)]])
            listKey.append(str([listKeyL[0][0],listKeyL[1][0],listKeyL[2][0],listKeyL[3][0],listKeyL[4][0]]))
            i = 0
            j = 1
            w = 3
            z = 2
            while i < 5:
                tmp = listKeyL[i][0]
                while j < 5:
                    listKey.append(str([tmp,listKeyL[j][0]]))
                    while z < 5:
                        listKey.append(str([tmp,listKeyL[j][0],listKeyL[z][0]]))
                        while w < 5:
                            listKey.append(str([tmp,listKeyL[j][0],listKeyL[z][0],listKeyL[w][0]]))
                            w+=1
                        z+=1
                        w=z+1
                    j+=1
                    z=j+1
                    w=z+1
                i+=1
                j=i+1
                z=j+1
                w=z+1
            listKey = sorted(listKey, key=len)
            keyAndNumber = [(key,len(k[key])) for key in sorted(k.keys(), key=len)]
            completeKeyNumber = {}
            for key in listKey:
                if key in [elem[0] for elem in keyAndNumber]:
                    completeKeyNumber[key] = keyAndNumber[[elem[0] for elem in keyAndNumber].index(key)][1]
                else:
                    completeKeyNumber[key] = 0
            #print(completeKeyNumber)
            dictLabels = {
                '00001': completeKeyNumber[listKey[0]],
                '00010': completeKeyNumber[listKey[1]],
                '00011': int(completeKeyNumber[listKey[5]]/2),
                '00100': completeKeyNumber[listKey[2]],
                '00101': int(completeKeyNumber[listKey[6]]/2),
                '00110': int(completeKeyNumber[listKey[9]]/2),
                '00111': int(completeKeyNumber[listKey[15]]/3),
                '01000': completeKeyNumber[listKey[3]],
                '01001': int(completeKeyNumber[listKey[7]]/2),
                '01010': int(completeKeyNumber[listKey[10]]/2),
                '01011': int(completeKeyNumber[listKey[16]]/3),
                '01100': int(completeKeyNumber[listKey[12]]/2),
                '01101': int(completeKeyNumber[listKey[18]]/3),
                '01110': int(completeKeyNumber[listKey[21]]/3),
                '01111': int(completeKeyNumber[listKey[25]]/4),
                '10000': completeKeyNumber[listKey[4]],
                '10001': int(completeKeyNumber[listKey[8]]/2),
                '10010': int(completeKeyNumber[listKey[11]]/2),
                '10011': int(completeKeyNumber[listKey[17]]/3),
                '10100': int(completeKeyNumber[listKey[13]]/2),
                '10101': int(completeKeyNumber[listKey[19]]/3),
                '10110': int(completeKeyNumber[listKey[22]]/3),
                '10111': int(completeKeyNumber[listKey[26]]/4),
                '11000': int(completeKeyNumber[listKey[14]]/2),
                '11001': int(completeKeyNumber[listKey[20]]/3),
                '11010': int(completeKeyNumber[listKey[23]]/3),
                '11011': int(completeKeyNumber[listKey[27]]/4),
                '11100': int(completeKeyNumber[listKey[24]]/3),
                '11101': int(completeKeyNumber[listKey[28]]/4),
                '11110': int(completeKeyNumber[listKey[29]]/4),
                '11111': int(completeKeyNumber[listKey[30]]/5),
            }
            v = vennD.venn5(dictLabels, names=[listKeyL[4][0],listKeyL[3][0],listKeyL[2][0],listKeyL[1][0],listKeyL[0][0]])
            nameUnifyGenes = str(listKeyL[0][0]) +'_'+ str(listKeyL[1][0]) +'_'+ str(listKeyL[2][0]) +'_'+ str(listKeyL[3][0]) +'_'+ str(listKeyL[4][0])
            nameF = nameF.replace("<", "_")
            nameF = nameF.replace(">", "_")
            nameUnifyGenes = nameUnifyGenes.replace("<", "_")
            nameUnifyGenes = nameUnifyGenes.replace(">", "_")
            plt.savefig(nameDir+str(listForVenn.index(k))+'/venn.png')
            print('Create: \''+str(listForVenn.index(k))+'/venn.png\'')
        plt.clf()
        plt.close()

#Draw histogram graph of common genes
def printHistogram(listCommonGenes, listFiles, nameDir, isNotFantom, isoformInEdge):
    for l in listCommonGenes:
        #if len([a for a in l[1:] if a[0] not in l[0] or a[2] not in l[0]]) > 0:
            listFrel = []
            for k in l[0]:
                listFrel.append([k])
            i = 1
            while i < len(l):
                listFrel[[u[0] for u in listFrel].index(l[i][0])].append(l[i][3])
                i += 1
            if 1 not in [len(k) for k in listFrel]:
                frelOriginalFile = []
                for name in [u[0] for u in listFiles]:
                    if isNotFantom:
                        if name in [u[0] for u in listFrel]:
                            tmp = [name]
                            for u in listFiles:
                                if u[0] == name:
                                    tmp = tmp + [k[2] for k in u[1:]]
                            frelOriginalFile.append(tmp)
                    else:
                        #find isoform we need to use
                        edgesNodes = [(u[0], u[1]) for u in isoformInEdge]
                        i = 0
                        j = 1
                        isoformToSearch = []
                        numberEdgesBetweenGeneCouple = 0
                        while i < len([u[0] for u in listFrel]):
                            numberEdgesBetweenGeneCouple += len([u[0] for u in listFrel])-i-1
                            while j < len([u[0] for u in listFrel]):
                                if ([u[0] for u in listFrel][i], [u[0] for u in listFrel][j]) in edgesNodes:
                                    isoformToSearch.append((isoformInEdge[edgesNodes.index(([u[0] for u in listFrel][i], [u[0] for u in listFrel][j]))])[2:])
                                if ([u[0] for u in listFrel][j], [u[0] for u in listFrel][i]) in edgesNodes:
                                    isoformToSearch.append((isoformInEdge[edgesNodes.index(([u[0] for u in listFrel][j], [u[0] for u in listFrel][i]))])[2:])
                                j += 1
                            i += 1
                            j = i+1
                        listNameIsoform = {}
                        #save name isoform of lists in a dictionary to improve the performance
                        for isoS in isoformToSearch:
                            for n in isoS:
                                tmpIsoform = n.split('<-->')
                                for iso in tmpIsoform:
                                    listNameIsoform[iso] = ((re.search(r'@\w*', iso)).group())[1:]
                        if len(listNameIsoform)==0:
                            if name.split('@')[1] in [u[0] for u in listFrel]:
                                listNameIsoform[name]=name.split('@')[1]
                        if (name.split('@'))[1] in [u[0] for u in listFrel] and (name.split('@'))[1] not in [u[0] for u in frelOriginalFile] and name in listNameIsoform:
                            tmp = [(name.split('@'))[1]]
                            for u in listFiles:
                                if u[0] == name:
                                    tmp = tmp + [k[2] for k in u[1:]]
                            frelOriginalFile.append(tmp)
                        elif (name.split('@'))[1] in [u[0] for u in listFrel] and (name.split('@'))[1] in [u[0] for u in frelOriginalFile] and name in listNameIsoform:
                            tmp = frelOriginalFile[[u[0] for u in frelOriginalFile].index((name.split('@'))[1])]
                            for u in listFiles:
                                if u[0] == name:
                                    tmp = tmp + [k[2] for k in u[1:]]
                            frelOriginalFile[[u[0] for u in frelOriginalFile].index((name.split('@'))[1])] = tmp
                listFrel = sorted(listFrel, key=ut.ord)
                frelOriginalFile = sorted(frelOriginalFile, key=ut.ord)
                #Prepare parameters to draw the histograms
                num_rows = int((float(len(listFrel))-0.1)/2)+1
                if num_rows == 1:
                    num_rows+=1;
                num_bins = 20
                fig, axes = plt.subplots(num_rows, 2, tight_layout=True)

                #Draw each histograms
                counter = 0
                for i in range(num_rows):
                    for j in range(2):
                        ax = axes[i][j]
                        # Plot when we have data
                        if counter < len(listFrel):
                            #Draw histogram with linear axes
                            ax.hist([frelOriginalFile[counter][1:], listFrel[counter][1:]], bins=num_bins, range=[0.0, 1.0], edgecolor='black', linewidth=1.2, color=['green', 'blue'], alpha=0.5, label=[str(listFrel[counter][0])+' original list', str(listFrel[counter][0])+' analyzed genes'])
                            # ax.hist(frelOriginalFile[counter][1:], bins=num_bins, density=True, edgecolor='black', linewidth=1.2, color='green', alpha=0.5, label='{}'.format(listFrel[counter][0]))
                            # ax.hist(listFrel[counter][1:], bins=num_bins, density=True, edgecolor='black', linewidth=1.2, color='blue', alpha=0.5, label='{}'.format(listFrel[counter][0]))
                            ax.set_xlabel('Frequency')
                            ax.set_ylabel('Number genes')
                            leg = ax.legend(loc='upper left')
                            leg.draw_frame(False)
                        # Remove axis when we no longer have data
                        else:
                            ax.set_axis_off()
                        counter += 1

                nameF = utex.buildNamefile(l)
                #create dir for each couple of genes
                nameDirGenes = nameDir+str(listCommonGenes.index(l))+'/'
                # tmp = plt.gcf().get_size_inches()
                plt.gcf().set_size_inches(15, 10)
                nameF = nameF.replace("<", "_")
                nameF = nameF.replace(">", "_")
                plt.savefig(nameDirGenes+'histogram.png')
                print('Create: \''+nameDirGenes+'histogram.png\'')
                # plt.gcf().set_size_inches(tmp)
                plt.clf()
                plt.close()
            else:
                print('No histogram printable')
