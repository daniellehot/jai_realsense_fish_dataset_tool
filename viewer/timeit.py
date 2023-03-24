if __name__=="__main__":
    create_folders()
    viewer = Viewer()
    durations = []
    try:
        viewer.start_stream()
        i = 0
        while viewer.jai_cam.Streaming and viewer.rs_cam.Streaming:
            start = time.time()
            print("Iteration", i)
            #print("V: Jai GO FPS", viewer.jai_cam.FrameRate, " Bandwidth ", viewer.jai_cam.BandWidth, " Mb/s", end='\r', flush=True)
            if not viewer.saved:
                viewer.retrieve_measures()
            else:
                viewer.retrieve_only_RGB()
            viewer.show()
            cv.waitKey(1)
            stop = time.time()
            durations.append(stop-start)
            i += 1
            if i == 100:
                viewer.stop_stream()

        duration_avg = np.average(np.asarray(durations))
        print("V: Average iteration duration", duration_avg)
        print("V: One of the cameras is not streaming.")
        print("   Streaming tatus Jai ", viewer.jai_cam.Streaming)
        print("   Status RealSense ", viewer.rs_cam.Streaming)
        if viewer.jai_cam.Streaming:
            viewer.jai_cam.CloseAndDisconnect()
        if viewer.rs_cam.Streaming:
            viewer.rs_cam.stop_streaming()

    except Exception as e:
        print("V: Error occured, stopping streams and shutting down")
        print("V: ", e)
        if viewer.jai_cam.Streaming:
            viewer.jai_cam.CloseAndDisconnect()
        if viewer.rs_cam.Streaming:
            viewer.rs_cam.stop_streaming()