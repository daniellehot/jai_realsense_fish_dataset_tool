void JaiGo::SaveImage(const string path)
{
    PvBufferWriter ImgWriter;
    PvBufferConverterRGBFilter ColorFilter;
    ColorFilter.SetGainR(1.4f);
    ColorFilter.SetGainG(1);
    ColorFilter.SetGainB(3.4f);
    ImgWriter.GetConverter().SetRGBFilter(ColorFilter);
    ImgWriter.GetConverter().SetBayerFilter(PvBayerFilterSimple);

    PvBuffer *lBuffer = NULL;
    PvResult lOperationResult;
    PvResult lPipelineResult = this->Pipeline->RetrieveNextBuffer( &lBuffer, 1000, &lOperationResult );

    if ( lPipelineResult.IsOK() && lOperationResult.IsOK() )
    {
        PvResult lResult;
        cout << "JAI: Saving image to " << path << endl;
        if (path.find("bmp") != string::npos)
        {
            lResult = ImgWriter.Store(lBuffer, path.c_str(), PvBufferFormatBMP);
        }
        else if (path.find("tiff") != string::npos)
        {
            lResult = ImgWriter.Store(lBuffer, path.c_str(), PvBufferFormatTIFF);
            //lResult = ImgWriter.Store(lBufferColored, "test_RGB12.tiff", PvBufferFormatTIFF);
        }
        else if (path.find("raw") != string::npos)
        {
            lResult = ImgWriter.Store(lBuffer, path.c_str(), PvBufferFormatRaw);
        }

        if ( lResult.IsFailure() ) 
        {
            cout <<"    JAI ERROR: Could not save the image."<<endl;
            cout <<"    JAI ERROR: "<<lResult.GetCodeString().GetAscii()<<endl;
            cout <<"    JAI ERROR: "<<lResult.GetDescription().GetAscii()<<endl;
        }
    
        this->Pipeline->ReleaseBuffer(lBuffer);
    }
}