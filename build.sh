#!/bin/bash
# a function to get user confirmation
confirm() {
	local answer
	local message=${1-"Are you sure?"}
	echo "$message [Y/N] => "
	read -n 1 -s answer
	case $answer in
		[yY])
			return 0
			;;
		*)
			return -1
			;;
	esac
}

if [ $# -ne 1 ]; then
	echo "Usage $0 [animation_script.json]"
	exit -1
fi
animation_script=$1
if [ ! -f "$animation_script" ]; then
	echo $animation_script does not exist.
	exit -1
fi
animation_name=${animation_script##*/}
animation_name=${animation_name%.*}
scene_data_dir=scenes/$animation_name/scene_data
scene_images_dir=scenes/$animation_name/scene_images
video_path=scenes/$animation_name/output.mp4

echo animation_name: $animation_name

if [ ! -d $scene_data_dir ] ||
	confirm "$scene_data_dir already has $(ls -l $scene_data_dir | wc -l) frame files. Rebuild frame data?"; then
	mkdir -p $scene_data_dir
	echo building frame data...
	echo python3 build_frames.py $animation_script $scene_data_dir
	python3 build_frames.py $animation_script $scene_data_dir
	if [ $? -ne 0 ]; then
		echo failed building frame data.
		exit -2
	fi
	echo frame data written to $scene_data_dir
fi

if [ ! -d $scene_images_dir ] ||
	confirm "$scene_images_dir already has $(ls -l $scene_images_dir | wc -l) frame images. Rebuild frame images?"; then
	mkdir -p $scene_images_dir
	echo building frame images...
	echo dart raytrace.dart $scene_data_dir $scene_images_dir
	dart raytrace.dart $scene_data_dir $scene_images_dir
	if [ $? -ne 0 ]; then
		echo failed building frame images.
		exit -2
	fi
	echo frame images written to $scene_images_dir
fi

if confirm "Build video to $video_path?"; then
	echo building video...
	echo ffmpeg -r 1 -pattern_type glob -i "${scene_images_dir}/*.ppm" \
		   -vcodec libx264 -crf 15 -pix_fmt yuv420p $video_path
	ffmpeg -r 1 -pattern_type glob -i "${scene_images_dir}/*.ppm" \
		   -vcodec libx264 -crf 15 -pix_fmt yuv420p $video_path
	if [ $? -ne 0 ]; then
		echo failed building video.
		exit -2
	fi
	echo video written to $video_path
fi
