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

mkdir -p $scene_data_dir
echo building frame data...
echo python3 build_frames.py $animation_script $scene_data_dir
python3 build_frames.py $animation_script $scene_data_dir
echo frame data written to $scene_data_dir

mkdir -p $scene_images_dir
echo building frame images...
echo dart raytrace.dart $scene_data_dir $scene_images_dir
dart raytrace.dart $scene_data_dir $scene_images_dir
echo frame images written to $scene_images_dir

echo building video...
echo ffmpeg -r 1 -pattern_type glob -i "${scene_images_dir}/*.ppm" \
       -vcodec libx264 -crf 15 -pix_fmt yuv420p $video_path
ffmpeg -r 1 -pattern_type glob -i "${scene_images_dir}/*.ppm" \
       -vcodec libx264 -crf 15 -pix_fmt yuv420p $video_path
echo video written to $video_path

