import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import networks as nw
import plotly.graph_objects as go
from collections import defaultdict
import scvelo as scv
import pyemma.msm as msm
import scipy
import scanpy as sc

def plot_top_genes(adata, top_genes = 6, ncols = 2, figsize = (8,8), color_map = 'tab10', color ='attractor', attractor = None, hspace = 0.5,wspace = 0.5):
    K = adata.obsm['rho'].shape[1]
    cmp = sns.color_palette(color_map, K)
    U = adata.layers['Mu']
    S = adata.layers['Ms']
    
    gene_sort = adata.var['r2_test'].sort_values(ascending=False).index.tolist()

    # calculate number of rows
    nrows = top_genes // ncols + (top_genes % ncols > 0)

    plt.figure(figsize=figsize)
    plt.subplots_adjust(hspace=hspace,wspace = wspace)
    
    for gene_id in range(top_genes):

        gene_name =  gene_sort[gene_id]
        ind_g = adata.var_names.tolist().index(gene_name)

        par = adata.uns['par'][ind_g,:]
        alpha = par[0:K]
        beta = par[K]


        ax = plt.subplot(nrows, ncols, gene_id + 1)
        
        if color == 'attractor':
            scv.pl.scatter(adata, x = S[:,ind_g],y = U[:,ind_g],color = 'attractor',show=False,alpha = 0.5,size = 50,ax=ax)
        if color == 'membership':
            scv.pl.scatter(adata, x = S[:,ind_g],y = U[:,ind_g],color = adata.obsm['rho'][:,attractor] ,show=False,size = 20,ax=ax)
        ax.axline((0, 0), slope=1/beta,color = 'k')
        ax.set_title(gene_name)
        for i in range(K):
            ax.axline((0, alpha[i]/beta), slope=0, color = cmp[i])

def plot_genes_list(adata, genelist, ncols = 2, figsize = (8,8), color_map = 'tab10',hspace = 0.5,wspace = 0.5):
    K = adata.obsm['rho'].shape[1]
    cmp = sns.color_palette(color_map, K)
    U = adata.layers['Mu']
    S = adata.layers['Ms']
    
    # calculate number of rows
    nrows = len(genelist) // ncols + (len(genelist) % ncols > 0)

    plt.figure(figsize=figsize)
    plt.subplots_adjust(hspace=hspace,wspace = wspace)
    
    for gene_id in range(len(genelist)):

        gene_name =  genelist[gene_id]
        ind_g = adata.var_names.tolist().index(gene_name)

        par = adata.uns['par'][ind_g,:]
        alpha = par[0:K]
        beta = par[K]


        ax = plt.subplot(nrows, ncols, gene_id + 1)
        scv.pl.scatter(adata, x = S[:,ind_g],y = U[:,ind_g],color = 'attractor',show=False,alpha = 0.5,size = 20,ax=ax)
        ax.axline((0, 0), slope=1/beta,color = 'k')
        ax.set_title(gene_name)
        for i in range(K):
            ax.axline((0, alpha[i]/beta), slope=0, color = cmp[i])
    
            
def plot_para_hist(adata, bins = 20, log = True,figsize = (8,8)):
    gene_select = [x in adata.uns['gene_subset'] for x in adata.var_names]
    par = adata.uns['par']
    K = par.shape[1]
    fig, axs = plt.subplots(1, K, sharex=True, sharey=True, tight_layout=False, squeeze = True, figsize = figsize)

    if log:
        par = np.log10(par)
    
    for i in range(K):
        if i<K-1:
            title_name = 'alpha'+str(i)
            color = None
        else:
            title_name = 'beta'
            color = 'g'
        axs[i].hist(par[:,i],density = True, bins = bins, color = color)
        axs[i].set_xlabel('log(parameter)')
        axs[i].set_ylabel('density')
        axs[i].set_title(title_name)


def plot_sankey(vector1, vector2):
    # Ensure both vectors have the same length.
    assert len(vector1) == len(vector2)

    label_dict = defaultdict(lambda: len(label_dict))
    
    # Generate a palette of colors.
    palette = sns.color_palette('husl', n_colors=len(set(vector1 + vector2))).as_hex()
    color_list = []

    for label in vector1 + vector2:
        label_id = label_dict[label]
        if len(color_list) <= label_id:
            color_list.append(palette[label_id % len(palette)])

    source = [label_dict[label] for label in vector1]
    target = [label_dict[label] for label in vector2]
    value = [1] * len(vector1)  # Assume each pair has a value of 1.
    
    # Color the links according to their target node.
    link_color = [color_list[target[i]] for i in range(len(target))]

    # Create the Sankey diagram.
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=list(label_dict.keys()),
            color=color_list
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_color  # Color the links.
        )
    )])

    fig.update_layout(title_text="Sankey Diagram", font_size=20)
    fig.show()        
                
def compute_tensor_similarity(adata, adata_aggr, pathway1, pathway2, state = 'spliced', attractor = None):
    if attractor == None:
        velo =  adata.obsm['tensor_v_aver'].copy()
    else:
        velo = adata.obsm['tensor_v'][:,:,:,attractor].copy()
    
    if state == 'spliced':
        vkey = 'vs'
        xkey = 'Ms'
    if state == 'unspliced':
        vkey = 'vu'
        xkey = 'Mu'
    if state == 'joint':
        print("check that the input includes aggregated object") # some problem needs fixed
        adata_aggr.layers['vj'] = np.concatenate((velo[:,:,0],velo[:,:,1]),axis = 1)
        vkey = 'vj'
        xkey = 'Ms'

    scv.tl.velocity_graph(adata, vkey = vkey, xkey = xkey, gene_subset = pathway1,n_jobs = -1)
    tpm1 = adata.uns[vkey+'_graph'].toarray()
    scv.tl.velocity_graph(adata, vkey = vkey, xkey = vkey, gene_subset = pathway2,n_jobs = -1)
    tpm2 = adata.uns[vkey+'_graph'].toarray()
    return np.corrcoef(tpm1.reshape(-1),tpm2.reshape(-1))[0,1]

def plot_landscape(sc_object,show_colorbar = False, dim = 2, size_point = 3, alpha_land = 0.5, alpha_point = 0.5,  color_palette_name = 'Set1', contour_levels = 15, elev=10, azim = 4):
    land_value = sc_object.uns['land_out']['land_value']
    xv = sc_object.uns['land_out']['grid_x']
    yv = sc_object.uns['land_out']['grid_y']
    trans_coord = sc_object.uns['land_out']['trans_coord'] 
    land_cell = sc_object.obs['land_cell']
    
    K = sc_object.obsm['rho'].shape[1]
    labels =sc_object.obs['attractor'].astype(int)
    
    color_palette = sns.color_palette(color_palette_name, K)
    cluster_colors = [color_palette[x] for x in labels]
    
    if dim == 2:
        plt.contourf(xv, yv, land_value, levels=contour_levels, cmap="Greys_r",zorder=-100, alpha = alpha_land)
        plt.scatter(*trans_coord.T, s=size_point, linewidth=0, c=cluster_colors, alpha=alpha_point)

    else:
        ax = plt.axes(projection='3d')
        ax.scatter(*trans_coord.T,land_cell,s=size_point, linewidth=0, c=cluster_colors, alpha=alpha_point)
        ax.plot_surface(xv, yv,land_value,rstride=1, cstride=1, linewidth=0, antialiased=True,cmap="Greys_r", alpha = alpha_land, vmin = 0, vmax=np.nanmax(land_value), shade = True)
        ax.grid(False)
        ax.axis('off')
        ax.view_init(elev=elev, azim=azim)
        
    if show_colorbar:
        plt.colorbar()
        

def infer_lineage(sc_object,si=0,sf=1,method = 'MPFT',flux_fraction = 0.9, size_state = 0.1, size_point = 3, alpha_land = 0.5, alpha_point = 0.5, size_text=20, show_colorbar = False, color_palette_name = 'Set1', contour_levels = 15):


    K = sc_object.obsm['rho'].shape[1]
    centers = sc_object.uns['land_out']['cluster_centers']

    

    P_hat = sc_object.uns['da_out']['P_hat']
    M = msm.markov_model(P_hat)
    mu_hat = M.pi
    
    if method == 'MPFT':
        Flux_cg = np.diag(mu_hat.reshape(-1)).dot(P_hat)
        max_flux_tree = scipy.sparse.csgraph.minimum_spanning_tree(-Flux_cg)
        max_flux_tree = -max_flux_tree.toarray()
        #for i in range(K):
        #    for j in range(i+1,K):   
        #        max_flux_tree[i,j]= max(max_flux_tree[i,j],max_flux_tree[j,i])
        #        max_flux_tree[j,i] = max_flux_tree[i,j]
        
        nw.plot_network(max_flux_tree, pos=centers, state_scale=size_state, state_sizes=mu_hat, arrow_scale=2.0,arrow_labels= None, arrow_curvature = 0.2, ax=plt.gca(),max_width=1000, max_height=1000)
        plot_landscape(sc_object, show_colorbar = show_colorbar, size_point = size_point, alpha_land = alpha_land, alpha_point = alpha_point,  color_palette_name = color_palette_name)
        plt.axis('off')   

        
    if method == 'MPPT':
        
        #state_reorder = np.array(range(K))
        #state_reorder[0] = si
        #state_reorder[-1] = sf
        #state_reorder[sf+1:-1]=state_reorder[sf+1:-1]+1
        #state_reorder[1:si]=state_reorder[1:si]-1
        if isinstance(si,int):
            si = list(map(int, str(si)))
        
        if isinstance(sf,int):
            sf = list(map(int, str(sf)))
        
        
        tpt = msm.tpt(M, si, sf)
        Fsub = tpt.major_flux(fraction=flux_fraction)
        Fsubpercent = 100.0 * Fsub / tpt.total_flux
        
    
        plot_landscape(sc_object, show_colorbar = show_colorbar, size_point = size_point, alpha_land = alpha_land, alpha_point = alpha_point,  color_palette_name = color_palette_name, contour_levels = contour_levels)
        nw.plot_network(Fsubpercent, state_scale=size_state*mu_hat,pos=centers, arrow_label_format="%3.1f",arrow_label_size = size_text,ax=plt.gca(), max_width=1000, max_height=1000)
        plt.axis('off')   


def plot_tensor_heatmap(adata, attractor = 'all', component = 'spliced', top_genes = 50):
    gene_sort = adata.var['r2_test'].sort_values(ascending=False).index.tolist()
    if component == 'unspliced':
        component_ind = 0
    else:
        component_ind = 1

    if attractor == 'all':
        adata.layers['velo_plot'] = adata.obsm['tensor_v_aver'][:,:,component_ind]
    else:
        adata.layers['velo_plot'] = adata.obsm['tensor_v'][:,:,component_ind,attractor]
    sc.pl.heatmap(adata, gene_sort[0:top_genes], groupby='attractor', layer = 'velo_plot',standard_scale = 'var',cmap='RdBu_r')
    plt.suptitle('Tensor of ' + component + ', Attractor '+str(attractor))
    plt.show()