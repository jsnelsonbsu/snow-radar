#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
import scipy.io

from Xsmurf_functions import *


# In[ ]:


args = sys.argv # grab input arguments ################

rdpath = args[1]; outpath = args[2] # full paths to folders
Isurf_min = int(args[3]) # minimum depth of surface picks (in index number)
Isurf_max = int(args[4]) # maximum depth of surface picks (in index number)
wtmm_scale = int(args[5]) # list of wtmm scales to test
size_thresh = int(args[6]) # list of chain size minimums to test
mod_thresh_multiplier = float(args[7]) # minimum modulus value (as a fraction of the mean in the entire image)
# (e.g., 1 = mean, 1.5 = 150% of the mean value, 0.8 = 80% of the mean)
#########################################################


# In[3]:


# LOAD FILES FROM RDPATH
stitched_rd_file = 'preprocessed_stitched_rd.npy' # standard stitched radargram array filename
stitched_xs_file = 'preprocessed_stitched_rd_xs.npy' # standard stitched x-coord filename
stitched_ys_file = 'preprocessed_stitched_rd_ys.npy' # standard stitched y-coord filename
all_rd = np.load(rdpath+stitched_rd_file)
xs_flattened = np.load(rdpath+stitched_xs_file)
ys_flattened = np.load(rdpath+stitched_ys_file)

# if output folder does not exist, make it:
if not os.path.exists(outpath):
    os.mkdir(outpath)
    print(outpath+' folder created.')


# In[2]:


# grab TWT
TWT_df = pd.read_csv(rdpath+'TWT_vector.csv')
TWT = np.array(TWT_df.TWT)
# In[10]:


hmin_idx = all_rd.shape[0] # use the vertical dimension of the stitched radargram to split into square chunks
hsplit_idxs = np.arange(0, all_rd.shape[1], hmin_idx)
hsplit_idxs = hsplit_idxs[1:] # grab split locations

counter = 1
for i in range(0, len(hsplit_idxs)): 
    # split radargrams and coordinates
    if i == len(hsplit_idxs): # for the last split, include all the way to the end of the all_rd
        rd_split = all_rd[:,hsplit_idxs[i]:all_rd.shape[1]] 
        xs_split = xs_flattened[hsplit_idxs[i]:all_rd.shape[1]] # x coordinates
        ys_split = ys_flattened[hsplit_idxs[i]:all_rd.shape[1]] # y coordinates
    else: # for all others:
        rd_split = all_rd[:,hsplit_idxs[i]:hsplit_idxs[i+1]]
        xs_split = xs_flattened[hsplit_idxs[i]:hsplit_idxs[i+1]] # x coordinates
        ys_split = ys_flattened[hsplit_idxs[i]:hsplit_idxs[i+1]] # y coordinates

#     # show the split radargram
#     fig, ax1 = plt.subplots(1,figsize=(6,6))
#     ax1.imshow(rd_split, vmin=np.percentile(rd_split,50), vmax=np.percentile(rd_split,100), cmap='Greys_r')
#     ax1.set_title('preprocessed rd')
#     plt.show()

    radargram = rd_split; radargram[radargram < np.percentile(radargram,50)] = np.percentile(radargram,50)

    # export radaragram if it doesn't exist:
    if not os.path.exists(rdpath+'rd'+str(counter).zfill(2)+'_preprocessed.npy'):
        np.save(rdpath+'rd'+str(counter).zfill(2)+'_preprocessed.npy', radargram)
    else:
        print('rd saved already.')
        
    # create coordinates output folder if it doesn't exist:
    if not os.path.exists(outpath+'coords/'):
        os.mkdir(outpath+'coords/')
        
    # WTMM ANALYSIS:
    rd_depth_xs = []; rd_depth_ys = []; rd_surf_idxs = []; rd_ground_idxs = []; rd_x_idxs = []; rd_TWT_surf = []; rd_TWT_ground = []; rd_ids = []
    print('rd'+str(counter).zfill(2)+'_'+str(wtmm_scale)+'scale_'+str(size_thresh)+'size_'+str(mod_thresh_multiplier)+'mod')
    if os.path.exists(outpath +'/coords/rd'+str(counter).zfill(2)+'_'+str(wtmm_scale)+'scale_'+str(size_thresh)+'size_'+str(mod_thresh_multiplier)+'mod.csv'):
        print('file exists. skipping to next:') # if parameter combo output already exists, skip it
    else:
        x_idxs = []; surf_idxs = []; ground_idxs = []; depths = [] # list of wtmm outputs

        # Run the WTMM
        [dx,dy,mm,m,a] = wtmm2d_v2(radargram,'gauss',wtmm_scale)  

        # # Visualize outputs from wtmm2d:
        # fig, axs = plt.subplots(2,3,figsize=(15,10))
        # axs[0,0].imshow(dx, aspect='equal', cmap = 'gray', interpolation='none'); axs[0,0].set_title('dx') # x gradient
        # axs[0,1].imshow(dy, aspect='equal', cmap = 'gray', interpolation='none'); axs[0,1].set_title('dy') # y gradient
        # axs[0,2].imshow(a, aspect='equal', cmap = 'gray', interpolation='none'); axs[0,2].set_title('a') # argument            
        # axs[1,0].imshow(mm, aspect='equal', cmap = 'gray', interpolation='none', vmin = np.min(mm), vmax = np.max(m)); 
        # axs[1,0].set_title('mm') # modulus maxima (interpolated)
        # axs[1,1].imshow(m, aspect='equal', cmap = 'gray', interpolation='none',vmin = np.min(mm), vmax = np.max(m));
        # axs[1,1].set_title('m') # modulus
        # axs[-1,-1].axis('off')
        # plt.show()

        # Chain the traces
        cmm = wtmmchains(mm,a,0,wtmm_scale,wtmm_scale/4) # chain at a specified scale (UNMASKED)

        # Filter chains based on size threshold
        cmm_passed = []
        mods = []
        for j in range(0, len(cmm)):
            if cmm[j].size > size_thresh: # adjust this condition to threshold
                cmm_passed.append(cmm[j])
                mods.append(cmm[j].linemeanmod) # collect mod information

        # Filter again based on gradient values (mean modulus)
        cmm_passed_2 = []
        # Filter chains based on size and mod threshold
        for k in range(0, len(cmm_passed)):
               if cmm_passed[k].linemeanmod > np.nanmean(mods)*mod_thresh_multiplier:
                cmm_passed_2.append(cmm_passed[k])

        # STRATEGY TO GRAB FIRST RETURNS FROM CHAINS
        xs = []; ys = [] # grab all chain coordinates
        for n in range(0, len(cmm_passed_2)):
            xs.extend(cmm_passed_2[n].ix); ys.extend(cmm_passed_2[n].iy)
        chain_coords = list(zip(xs,ys)); chain_coords.sort() # sort by xs
        [xs,ys] = zip(*chain_coords)
        xs = list(xs); ys = list(ys)

        # PLOT RESULTS:
        a=0.3
        fig,ax = plt.subplots(1,figsize=(15,5))
        ax.imshow(np.array(radargram),cmap='gray')
        ax.set_xlim([0, np.array(radargram).shape[1]])
        ax.set_ylim([0, np.array(radargram).shape[0]])
        ax.invert_yaxis(); ax.set_aspect('equal')

        # FOR EACH COLUMN GRAB FIRST AND SECOND RETURN AND SUBTRACT (ONLY IF THERE ARE AT LEAST TWO), WINDOW REMOVED
        for x_idx in range(0,radargram.shape[1]): 
            coord_idxs = np.where(np.array(xs) == x_idx)[0] # grab any chains in this column
            if len(coord_idxs) > 2: # if there are at least 2 crossings at the x
                cxs = []; cys = []
                for idx in coord_idxs: # for each chain crossing
                    cxs.append(xs[idx]); cys.append(ys[idx]) # grab the x and y coordinates

                # grab the first pair of ys that is > 1 apart
                diff_idxs = np.where(np.diff(cys) > 1)[0] # calculate the difference between the ys
                if len(diff_idxs) > 0: # if not empty
                    l=0
                    Isurf = int(cys[diff_idxs[l]]) # find the surface index
                    while Isurf < Isurf_min and l < len(diff_idxs): # while lower than the upper surface threshold, keep looking
                        Isurf = int(cys[diff_idxs[l]])
                        l+=1 # keep looping through the list until an Isurf is found
                    if Isurf >= Isurf_min and Isurf <= Isurf_max: # if it lays between search bounds
                        #look for ground index:
                        for i in np.flip(range(1, len(diff_idxs))): # loop from last index to second index
                            diff_last = diff_idxs[i]+1
                            Iground = int(cys[diff_last]) # select the ground index
                            if Iground >= Isurf_max and Iground <= (hmin_idx-20): # look below surface max
                                # do not look within 20 pixels of the edge
                                ax.plot(x_idx, Isurf, 'b.', alpha=a)# plot the surface return
                                ax.plot(x_idx, Iground, 'r.', alpha=a)# plot the ground return

                                rd_depth_xs.append(xs_split[x_idx]); rd_depth_ys.append(ys_split[x_idx])
                                rd_surf_idxs.append(Isurf); rd_ground_idxs.append(Iground)
                                rd_TWT_surf.append(TWT[Isurf]); rd_TWT_ground.append(TWT[Iground])
                                rd_x_idxs.append(x_idx); rd_ids.append('rd'+str(counter).zfill(2))
                                
                                break # stop looping through ground indexes
                    else: # if no returns found in the surface bounds, append NaNs
                        rd_depth_xs.append(np.NaN); rd_depth_ys.append(np.NaN)
                        rd_surf_idxs.append(np.NaN); rd_ground_idxs.append(np.NaN)
                        rd_TWT_surf.append(np.NaN); rd_TWT_ground.append(np.NaN)
                        rd_x_idxs.append(np.NaN); rd_ids.append('rd'+str(counter).zfill(2))
                else: # if only 1 or 0 crossings, append NaNs
                    rd_depth_xs.append(np.NaN); rd_depth_ys.append(np.NaN)
                    rd_surf_idxs.append(np.NaN); rd_ground_idxs.append(np.NaN)
                    rd_TWT_surf.append(np.NaN); rd_TWT_ground.append(np.NaN)
                    rd_x_idxs.append(np.NaN); rd_ids.append('rd'+str(counter).zfill(2))
        # write to CSV 
        export_df = pd.DataFrame(list(zip(rd_depth_xs, rd_depth_ys, rd_surf_idxs, rd_ground_idxs, rd_x_idxs, rd_TWT_surf, rd_TWT_ground, rd_ids)), 
                                 columns=['x','y','Isurf','Iground','rd_xidx', 'TWT_surf', 'TWT_ground', 'rd_id'])
        export_df.to_csv(outpath +'/coords/rd'+str(counter).zfill(2)+'_'+str(wtmm_scale)+'scale_'+str(size_thresh)+'size_'+str(mod_thresh_multiplier)+'mod.csv')
        ax.legend(['surface','ground'])
        plt.tight_layout() # display as figure
        plt.savefig(outpath +'rd'+str(counter).zfill(2)+'_'+str(wtmm_scale)+'scale_'+str(size_thresh)+'size_'+str(mod_thresh_multiplier)+'mod.jpg',dpi=200)
        plt.close()
    counter+=1 # count the split radargrams


# In[ ]:




