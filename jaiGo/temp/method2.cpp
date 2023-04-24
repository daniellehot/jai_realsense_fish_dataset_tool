void JaiGo::ConvertBuffer(PvBuffer *InputBuffer, PvBuffer *OutputBuffer, PvPixelType PixelFormat) 
{
    PvBufferConverter *Converter = new PvBufferConverter();
    PvBufferConverterRGBFilter *ColorFilter = new PvBufferConverterRGBFilter();
    ColorFilter->SetGainR(1.4f);
    ColorFilter->SetGainG(1);
    ColorFilter->SetGainB(3.4f);
    Converter->SetRGBFilter(*ColorFilter);
    Converter->SetBayerFilter(PvBayerFilterSimple); 

    if (Converter->IsConversionSupported(InputBuffer->GetImage()->GetPixelType(), PixelFormat))
    {
        OutputBuffer->GetImage()->Alloc(
            InputBuffer->GetImage()->GetWidth(), 
            InputBuffer->GetImage()->GetWidth(), 
            PixelFormat);
        Converter->Convert(InputBuffer, OutputBuffer, 1, 0);
    }
    else 
    {
        cout << "   JAI ERROR: Conversion is not supported" << endl;
    }

    //Clean up
    delete Converter;
    delete ColorFilter;
}

void JaiGo::SaveImage(const string path)
{
    PvBufferWriter ImgWriter;

    PvBuffer *lBuffer = NULL;
    PvResult lOperationResult;
    PvResult lPipelineResult = this->Pipeline->RetrieveNextBuffer( &lBuffer, 1000, &lOperationResult );

    if ( lPipelineResult.IsOK() && lOperationResult.IsOK() )
    {
        PvBuffer *lBufferColored = new PvBuffer(PvPayloadTypeImage);
        JaiGo::ConvertBuffer(lBuffer, lBufferColored, PvPixelRGB16);

        PvResult lResult;
        cout << "JAI: Saving image to " << path << endl;
        if (path.find("bmp") != string::npos)
        {
            lResult = ImgWriter.Store(lBufferColored, path.c_str(), PvBufferFormatBMP);
        }
        else if (path.find("tiff") != string::npos)
        {
            lResult = ImgWriter.Store(lBufferColored, path.c_str(), PvBufferFormatTIFF);
            //lResult = ImgWriter.Store(lBufferColored, "test_RGB12.tiff", PvBufferFormatTIFF);
        }
        else if (path.find("raw") != string::npos)
        {
            lResult = ImgWriter.Store(lBufferColored, path.c_str(), PvBufferFormatRaw);
        }

        if ( lResult.IsFailure() ) 
        {
            cout <<"    JAI ERROR: Could not save the image."<<endl;
            cout <<"    JAI ERROR: "<<lResult.GetCodeString().GetAscii()<<endl;
            cout <<"    JAI ERROR: "<<lResult.GetDescription().GetAscii()<<endl;
        }
    
        this->Pipeline->ReleaseBuffer(lBuffer);
        delete lBufferColored;
    }
}