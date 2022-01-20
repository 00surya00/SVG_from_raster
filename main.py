#!/bin/python3

import cv2 as cv;
import numpy as np;
import drawSvg as draw;
import math;

def ang(p1,p2):
	return math.degrees(math.atan2(p1[0]-p2[0],p1[1]-p2[1]));

def curvy_path_from_points(path,stroke):
	assert(len(path)>0);
	if(len(path)<2):
		return straight_line_from_points(path,stroke);
	n=len(path);
	my_path=draw.Path(stroke_width=1,stroke=stroke,fill='none');
	my_path.M(path[n-1][0],path[n-1][1]);
	path.pop();
	i=n-1;
	while(i>1):
		if(len(path)>=2):
			first=path.pop();
			second=path.pop();
			my_path.S(first[0],first[1],second[0],second[1]);
			cur_length=0;
			i-=2;
	if(i>=1):
		first=path.pop();
		my_path.T(first[0],first[1]);
	return my_path;

def straight_line_from_points(path,stroke):
	assert(len(path)>0);
	if(len(path)==1):
		return draw_point(path[0],stroke);
	n=len(path);
	my_path=draw.Path(stroke_width=1,stroke=stroke,fill='none');
	my_path.M(path[n-1][0],path[n-1][1]);
	path.pop();
	i=n-1;
	while(i>1):
		if(len(path)>0):
			first=path.pop();
			my_path.L(first[0],first[1]);
			i-=1;
	return my_path;

def draw_point(point,stroke):
	return draw.Circle(point[0],point[1],1,stroke_width=1,stroke=stroke);

if __name__=='__main__':
	work_count=0;
	deg_thres=30;
	sampling_rate=10;

	print('Reading image...');
	img_buf=cv.imread('input.png'); #Read image into memory
	#Exception
	if img_buf is None:
		print('Data format error or the file is not present');
		exit(65);
	print('Image read successfully!');



	print('Converting to gray scale');
	gray_scale=cv.cvtColor(img_buf,cv.COLOR_BGR2GRAY);
	print('Converted to gray scale!');



	print('Resizing image...');
	factor=1000/img_buf.shape[0];
	gray_scale=cv.resize(src=gray_scale,fx=factor,fy=factor,dsize=None);
	print('Resized image!');



	print('Applying gaussian to smoothen image...');
	cv.GaussianBlur(src=gray_scale,dst=gray_scale,ksize=(5,5),sigmaX=0,sigmaY=0);
	print('Applyied gaussian to smoothen image!');



	print('Enhancing image...');
	gray_scale=cv.convertScaleAbs(gray_scale, alpha=1.5, beta=0);
	print('Enhanced image!');
	cv.imwrite('enhanced.png',gray_scale);



	print('Finding the edges...');
	thin_edge=cv.Canny(gray_scale,50,130);
	print('Found the edges!');
	cv.imwrite('canny_output.png',thin_edge);



	print('Creating a set from edge points..');
	edge_points=set();
	for i in range(thin_edge.shape[0]):
		for j in range(thin_edge.shape[1]):
			if(thin_edge[i][j]==255):
				edge_points.add((i,j));
	print('Created a set containing '+str(len(edge_points))+' edge points');



	print('Tracing paths...');
	paths=[[]];
	possibilities=((1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1));
	point=(0,0);
	path_count=0;
	point_count=0;
	right_count=0;
	wrong_count=0;
	last_pos=1;
	path_threshold=5;
	points_bef=0;
	cur_length=1;
	for point in edge_points:
		edge_points.remove(point);
		paths[path_count].append(point);
		break;
	print('New path started...');
	while len(edge_points)>0:
		print('Point - '+str(point));
		point_count+=1;
		x=point[0];
		y=point[1];
		estim_x=x+possibilities[last_pos][0];
		estim_y=y+possibilities[last_pos][1];
		if (estim_x,estim_y) not in edge_points:
			print('Wrong estimation! '+str((estim_x,estim_y)));
			found=False;
			wrong_count+=1;
			last_pos=(last_pos-1)%8;
			for i in range(8):
				cur=(last_pos+i)%8;
				possibility=possibilities[cur];
				if (x+possibility[0],y+possibility[1]) in edge_points:
					estim_x=x+possibility[0];
					estim_y=y+possibility[1];
					found=True;
					last_pos=cur;
					break;
		else:
			found=True;
			right_count+=1;
			print('Right estimation! '+str((estim_x,estim_y)));
		if found:
			print('Next '+str((estim_x,estim_y)));
			point=(estim_x,estim_y);
			edge_points.remove(point);
			if(cur_length%sampling_rate==0):
				the_angle=abs(ang(paths[path_count][-sampling_rate+1],paths[path_count][int(-sampling_rate/2)]) - ang(paths[path_count][int(-sampling_rate/2)],point));
				print('The angle - ',the_angle);
				if the_angle <= deg_thres:
					print('Lets see the work -'+str(len(paths[path_count])));
					del paths[path_count][-sampling_rate+1:];
					work_count+=1;
					print('Yeah! it worked - '+str(len(paths[path_count])));
			paths[path_count].append(point);
			cur_length+=1;
		else:
			if point_count-points_bef<path_threshold:
				paths.pop();
			else:
				print('Path ended - '+str(path_count));
				path_count+=1;
			paths.append([]);
			for point in edge_points:
				edge_points.remove(point);
				paths[path_count].append(point);
				break;
			cur_length=1;
			print('New path started...');
			points_bef=point_count;
	print('Number of paths - '+str(path_count));
	print('Number of points - '+str(point_count));
	print('Right estimations - '+str(right_count));
	print('Wrong estimations - '+str(wrong_count));
	print('Work count - '+str(work_count));

	i=0;
	path_img=[];
	paths.pop();
	for path in paths:
		path_img.append(np.zeros(shape=gray_scale.shape,dtype=np.uint8));
		for point in path:
			path_img[i][point[0]][point[1]]=255;
		cv.imwrite(f"path{i}.png",path_img[i]);
		i+=1;
	
	sum_of_all_paths=np.zeros(shape=gray_scale.shape,dtype=np.uint8);
	for path in paths:
		for point in path:
			sum_of_all_paths[point[0]][point[1]]=255;
	cv.imwrite('canny_output.png',thin_edge);
	cv.imwrite('sum_of_all_paths.png',sum_of_all_paths);

	my_drawing=draw.Drawing(gray_scale.shape[0],gray_scale.shape[1],transform='rotate(90,0,300)');
	for path in paths:
			my_drawing.append(curvy_path_from_points(path,stroke='black'));
	my_drawing.saveSvg('final.svg');
