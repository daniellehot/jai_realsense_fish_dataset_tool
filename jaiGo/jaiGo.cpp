#include <PvSampleUtils.h>
#include <PvDevice.h>
#include <PvDeviceGEV.h>
#include <PvDeviceU3V.h>
#include <PvStream.h>
#include <PvStreamGEV.h>
#include <PvStreamU3V.h>
#include <PvBuffer.h>
#include <PvPipeline.h>
#include <PvConfigurationReader.h>
#include <PvBufferWriter.h>
#include <PvBufferConverter.h>
#include <PvGenParameterArray.h>
#include <PvGenParameter.h>

#include "opencv2/opencv.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <opencv2/imgcodecs.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;

#define BUFFER_COUNT ( 16 )
#define FILE_NAME ( "/home/vap/jai_realsense_fish_dataset_tool/jaiGo/writeReadConfiguration/test_config.pvxml" )
#define DEVICE_CONFIGURATION_TAG ( "DeviceConfiguration" )
#define STREAM_CONFIGURAITON_TAG ( "StreamConfiguration" )

class JaiGo {
    private:
        PvString ConnectionID;
        PvDevice *Device = NULL;
        PvGenParameterArray *DevParameters = NULL;
        PvStream *Stream = NULL;
        PvPipeline *Pipeline = NULL;

        //PvBuffer *ImgBuffer = NULL;
        //PvBufferConverter *Converter = new PvBufferConverter(); //remember to delete at the end

        PvGenCommand *StartCommand = NULL;
        PvGenCommand *StopCommand = NULL;
        PvGenFloat *FrameRate = NULL;
        PvGenFloat *Bandwidth = NULL;

        //Find and Connect
        bool FindDevice( PvString *aConnectionID);
        PvDevice *ConnectToDevice( const PvString &aConnectionID );
        
        //StartStream()
        PvStream *OpenStream( const PvString &aConnectionID );
        bool LoadCameraConfiguration(PvDevice *aDevice, PvStream *aStream);
        PvPipeline *CreatePipeline( PvDevice *aDevice, PvStream *aStream );

        //void ConvertBuffer(PvBuffer *InputBuffer, PvBuffer *OutputBuffer, PvPixelType PixelFormat); 
        //void ProcessBuffer(PvBuffer *Buffer);

        //Convert Buffer to cv::Mat and then convert cv::Mat to numpy array
        cv::Mat GetCvImage(PvBuffer *buffer, PvPixelType pixelFormat);
        py::dtype determine_np_dtype(int depth);
        std::vector<std::size_t> determine_shape(cv::Mat& m);
        py::capsule make_capsule(cv::Mat& m);
        py::array mat_to_nparray(cv::Mat& m);

    public:
        bool Connected = false;
        bool Streaming = false;

        bool LoadCustomCameraConfiguration = false;
        string CameraConfigurationPath;

        //Stream statistics
        double FrameRateVal = 0.0;
        double BandwidthVal = 0.0;

        //Gains
        bool AdjustColors = false;
        double GainB;
        double GainG;
        double GainR;  

        //Image
        int ImgWidth;
        int ImgHeight;
        //cv::Mat cvImg;
        py::array npImg;

        void FindAndConnect();
        void StartStream();
        void StopStream();
        bool GrabImage();
        bool SaveImage(const string path);
        void CloseAndDisconnect();

        bool SetPixelFormat(const string format);
};

void JaiGo::FindAndConnect()
{
    PvString lConnectionID;
    if (JaiGo::FindDevice(&lConnectionID))
    {   
        PvDevice *lDevice = NULL;
        lDevice = ConnectToDevice(lConnectionID);
        if (lDevice != NULL)
        {
            cout<<"JAI: Connection and Device Acquired"<<endl;
            this->ConnectionID = lConnectionID;
            this->Device = lDevice;
            this->DevParameters = lDevice->GetParameters();
            this->Connected = true;
        }
    }
}   

bool JaiGo::FindDevice( PvString *aConnectionID)
{
    PvResult lResult;
    const PvDeviceInfo *lSelectedDI = NULL;
    PvSystem lSystem;

    cout << endl << "JAI: Detecting devices." << endl;
    
    lSystem.Find();
    vector<const PvDeviceInfo *> lDIVector;
    for ( uint32_t i = 0; i < lSystem.GetInterfaceCount(); i++ )
    {
        const PvInterface *lInterface = dynamic_cast<const PvInterface *>( lSystem.GetInterface( i ) );
        if ( lInterface != NULL )
        {
            //cout << "   " << lInterface->GetDisplayID().GetAscii() << endl;
            for ( uint32_t j = 0; j < lInterface->GetDeviceCount(); j++ )
            {
                const PvDeviceInfo *lDI = dynamic_cast<const PvDeviceInfo *>( lInterface->GetDeviceInfo( j ) );
                if ( lDI != NULL )
                {
                    lDIVector.push_back( lDI );
                    //cout << "[" << ( lDIVector.size() - 1 ) << "]" << "\t" << lDI->GetDisplayID().GetAscii() << endl;
                }					
            }
        }
    }
    
    if ( lDIVector.size() == 0)
    {
        cout << "JAI: No device found!" << endl;
        return false;
    } else 
    {
        cout << "JAI: Found "<< lDIVector.size() << " devices. \n";
        for (uint i = 0; i < lDIVector.size(); i++)
        {
            cout << "   " << i << ") " <<lDIVector[i]->GetDisplayID().GetAscii()<<endl;
        }
        cout << "JAI: Connecting to " << lDIVector.back()->GetDisplayID().GetAscii()<<endl;
        *aConnectionID = lDIVector.back()->GetConnectionID();
        return true;
    }
}

PvDevice* JaiGo::ConnectToDevice( const PvString &aConnectionID )
{
    PvDevice *lDevice;
    PvResult lResult;
    lDevice = PvDevice::CreateAndConnect( aConnectionID, &lResult );
    if ( lDevice == NULL )
    {
        cout << "JAI: Unable to connect to device: "
        << lResult.GetCodeString().GetAscii()
        << " ("
        << lResult.GetDescription().GetAscii()
        << ")" << endl;
    }
 
    return lDevice;
}

void JaiGo::StartStream()
{
    PvStream *lStream = NULL;
    lStream = JaiGo::OpenStream(this->ConnectionID);
    if ( lStream != NULL )
    {
        this->Stream = lStream;

        bool DeviceAndStreamConfigurationReady = true; //With default setting this is always true
        if (this->LoadCustomCameraConfiguration)
        {
            DeviceAndStreamConfigurationReady = JaiGo::LoadCameraConfiguration(this->Device, this->Stream); //If a custom configuration is needed, errors might occur
        }
        
        if (DeviceAndStreamConfigurationReady)
        {
            PvPipeline *lPipeline = NULL;
            lPipeline = JaiGo::CreatePipeline(this->Device, lStream );
            if( lPipeline )
            {
                this->Pipeline = lPipeline;
                
                // Get device parameters needed to control streaming
                PvGenParameterArray *lDeviceParams = this->Device->GetParameters();

                // Map the GenICam AcquisitionStart and AcquisitionStop commands
                this->StartCommand = dynamic_cast<PvGenCommand *>( lDeviceParams->Get( "AcquisitionStart" ) );
                this->StopCommand = dynamic_cast<PvGenCommand *>( lDeviceParams->Get( "AcquisitionStop" ) );

                // Note: the pipeline must be initialized before we start acquisition
                cout << "JAI: Starting pipeline" << endl;
                this->Pipeline->Start();

                // Get stream parameters
                PvGenParameterArray *lStreamParams = this->Stream->GetParameters();

                // Map a few GenICam stream stats counters
                this->FrameRate = dynamic_cast<PvGenFloat *>( lStreamParams->Get( "AcquisitionRate" ) );
                this->Bandwidth = dynamic_cast<PvGenFloat *>( lStreamParams->Get( "Bandwidth" ) );

                // Enable streaming and send the AcquisitionStart command
                cout << "JAI: Enabling streaming and sending AcquisitionStart command." << endl;
                this->Device->StreamEnable();
                this->StartCommand->Execute();

                this->Streaming = true;
            }
        }
    }

}

void JaiGo::StopStream()
{
    this->Streaming = false;
}

PvStream* JaiGo::OpenStream( const PvString &aConnectionID )
{
    PvStream *lStream;
    PvResult lResult;

    // Open stream to the GigE Vision or USB3 Vision device
    cout << "JAI: Opening stream from device." << endl;
    lStream = PvStream::CreateAndOpen( aConnectionID, &lResult );
    if ( lStream == NULL )
    {
        cout << "JAI: Unable to stream from device." << endl;
    }

    return lStream;
}

bool JaiGo::LoadCameraConfiguration(PvDevice *aDevice, PvStream *aStream)
{
    PvConfigurationReader lReader;
    // Load all the information into a reader.
    cout << "JAI: Loading configuration" << endl;
    lReader.Load( this->CameraConfigurationPath.c_str() );

    cout << "JAI: Restoring device configuration" << endl;
    PvResult lResult = lReader.Restore( DEVICE_CONFIGURATION_TAG, aDevice);
    if ( !lResult.IsOK() )
    {
        cout << "JAI: "<<lResult.GetCodeString().GetAscii() << endl;
        return false;
    }

    cout << "JAI: Restoring stream configuration" << endl;
    lResult = lReader.Restore( STREAM_CONFIGURAITON_TAG, aStream);
    if ( !lResult.IsOK() )
    {
        cout << "JAI: "<<lResult.GetCodeString().GetAscii() << endl;
        return false;
    }

    return true;
}

PvPipeline* JaiGo::CreatePipeline( PvDevice *aDevice, PvStream *aStream )
{
    // Create the PvPipeline object
    PvPipeline* lPipeline = new PvPipeline( aStream );

    if ( lPipeline != NULL )
    {        
        // Reading payload size from device
        uint32_t lSize = aDevice->GetPayloadSize();
    
        // Set the Buffer count and the Buffer size
        lPipeline->SetBufferCount( BUFFER_COUNT );
        lPipeline->SetBufferSize( lSize );
    }
    
    return lPipeline;
}

/*
cv::Mat JaiGo::GetCvImage(PvBuffer *ImgBuffer)
{
    PvGenParameter *lParameter = this->DevParameters->Get( "PixelFormat" );
    PvGenEnum *lPixelFormatParameter = dynamic_cast<PvGenEnum *>( lParameter );
    PvString pixelFormat;
    PvResult lResult = lPixelFormatParameter->GetValue(pixelFormat);
    //cv::Mat cvImg(this->ImgBuffer->GetImage()->GetHeight(), this->ImgBuffer->GetImage()->GetWidth(), CV_8UC3);
    cv::Mat Img(ImgBuffer->GetImage()->GetHeight(), ImgBuffer->GetImage()->GetWidth(), CV_8UC3);
    

    if (lResult.IsOK())
    {
        if ( strcmp( pixelFormat.GetAscii(), "BayerRG8" ) == 0 )
        {
            cv::Mat cvMat = cv::Mat(ImgBuffer->GetImage()->GetHeight(), ImgBuffer->GetImage()->GetWidth(), CV_8U, ImgBuffer->GetDataPointer());
            cv::cvtColor(cvMat, Img, cv::COLOR_BayerRG2RGB);
        } 
        else if ( strcmp( pixelFormat.GetAscii(), "BayerRG10p" ) == 0 || strcmp( pixelFormat.GetAscii(), "BayerRG12p" ) == 0 )
        {
            cout << "JAI: Selected pixel format cannot be visualized. Use BayerRG8, BayerRG10, or BayerRG12. Current format is " << pixelFormat.GetAscii() << endl;
        }
        else
        {
            cv::Mat img16Bit = cv::Mat(ImgBuffer->GetImage()->GetHeight(), ImgBuffer->GetImage()->GetWidth(), CV_16U, ImgBuffer->GetDataPointer());
            cv::Mat img8Bit;
            img16Bit.convertTo(img8Bit, CV_8U, 0.0625f);
            cv::cvtColor(img8Bit, Img, cv::COLOR_BayerRG2RGB);   
        }
    }
    //this->cvImg = Img;

    return Img;
}
*/

/*
void JaiGo::ConvertBuffer(PvBuffer *InputBuffer, PvBuffer *OutputBuffer, PvPixelType PixelFormat) 
{
    PvBufferConverterRGBFilter *ColorFilter = new PvBufferConverterRGBFilter();
    ColorFilter->SetGainR(1.4f);
    ColorFilter->SetGainG(1.0f);
    ColorFilter->SetGainB(3.4f);
    PvBufferConverter *Converter = new PvBufferConverter();  
    Converter->SetBayerFilter(PvBayerFilterSimple); 
    Converter->SetRGBFilter(*ColorFilter);
    
    if (Converter->IsConversionSupported(InputBuffer->GetImage()->GetPixelType(), PixelFormat))
    {
        OutputBuffer->GetImage()->Alloc(
            InputBuffer->GetImage()->GetWidth(), 
            InputBuffer->GetImage()->GetHeight(), 
            PixelFormat
            );

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
*/

cv::Mat JaiGo::GetCvImage(PvBuffer *buffer, PvPixelType pixelFormat)
{
    PvBuffer *convertedBuffer = new PvBuffer();
    convertedBuffer->GetImage()->Alloc(
        buffer->GetImage()->GetWidth(), 
        buffer->GetImage()->GetHeight(), 
        pixelFormat
    );

    PvBufferConverter  *converter = new PvBufferConverter();
    converter->SetBayerFilter(PvBayerFilterSimple);
    
    if (converter->IsConversionSupported(buffer->GetImage()->GetPixelType(), pixelFormat))
    {
        converter->Convert(buffer, convertedBuffer, 1, 0);
    }
    else 
    {
        cout << "JAI ERROR: Conversion is not supported " << endl;
    }

    cv::Mat cvImg;
    if (pixelFormat == PvPixelBGR8)
    {
        cvImg = cv::Mat(convertedBuffer->GetImage()->GetHeight(), convertedBuffer->GetImage()->GetWidth(), CV_8UC3, convertedBuffer->GetDataPointer());
    }

    if (pixelFormat == PvPixelBGR16)
    {
        cvImg = cv::Mat(convertedBuffer->GetImage()->GetHeight(), convertedBuffer->GetImage()->GetWidth(), CV_16UC3, convertedBuffer->GetDataPointer());
    }

    if (this->AdjustColors)
    {
        cvImg = cvImg.mul( cv::Scalar(this->GainB, this->GainG, this->GainR) );
    }

    
    delete converter, convertedBuffer;
    return cvImg;
}


bool JaiGo::GrabImage()
{ 
    bool receivedImage = false;
    PvBuffer *lBuffer = NULL;
    PvResult lOperationResult;

    // Retrieve next buffer
    PvResult lResult = this->Pipeline->RetrieveNextBuffer( &lBuffer, 10, &lOperationResult );
    if ( lResult.IsOK() )
    {
        if ( lOperationResult.IsOK() )
        {
            // We now have a valid buffer. This is where you would typically process the buffer.
            this->FrameRate->GetValue( this->FrameRateVal );
            this->Bandwidth->GetValue( this->BandwidthVal );
            this->BandwidthVal /= 1000000.0; //Conversion to Mb 

            if (lBuffer->GetPayloadType() == PvPayloadTypeImage)
            {
                this->ImgWidth = lBuffer->GetImage()->GetWidth();
                this->ImgHeight = lBuffer->GetImage()->GetHeight();
                //this->ImgBuffer = lBuffer;
                //cv::Mat cvColorImg = JaiGo::GetCvImage(lBuffer);
                //cout << "Pixel type of the grabbed image " << PvImage::PixelTypeToString( lBuffer->GetImage()->GetPixelType() ).GetAscii() << endl;

                //this->cvImg = JaiGo::GetCvImage(lBuffer);
                cv::Mat cvImg = JaiGo::GetCvImage(lBuffer, PvPixelBGR8);
                this->npImg = JaiGo::mat_to_nparray(cvImg);
                receivedImage = true;
            } 
            else
            {
                cout<< "JAI: Incorrect payload type. Start stream with PvPayloadTypeImage. Current type is " << lBuffer->GetPayloadType() << endl;
            }
        }
        else
        {
            // Non OK operational result
            cout <<"JAI: "<<lOperationResult.GetCodeString().GetAscii() << endl;
        }

        // Release the buffer back to the pipeline
        this->Pipeline->ReleaseBuffer(lBuffer);
    }
    else
    {
        // Retrieve buffer failure
        if (lResult != PvResult::Code::TIMEOUT)
        {
            cout <<"JAI: "<<lResult.GetCodeString().GetAscii() << endl;
        }
    }

    return receivedImage;
}

/*
void JaiGo::ProcessBuffer(PvBuffer *Buffer)
{   
    cout << "Buffer Pixel type " << PvImage::PixelTypeToString( Buffer->GetImage()->GetPixelType() ).GetAscii() << endl;

    PvBufferConverter  *converter = new PvBufferConverter();
    converter->SetBayerFilter(PvBayerFilterSimple);
 
    //PvPixelType goalPixelFormat = PvPixelRGB16;
    PvBuffer *convertedBuffer = new PvBuffer();
    convertedBuffer->GetImage()->Alloc(
            Buffer->GetImage()->GetWidth(), 
            Buffer->GetImage()->GetHeight(), 
            PvPixelBGR16
            );

    converter->Convert(Buffer, convertedBuffer, 1, 0);
    cv::Mat Img = cv::Mat(convertedBuffer->GetImage()->GetHeight(), convertedBuffer->GetImage()->GetWidth(), CV_16UC3, convertedBuffer->GetDataPointer());
    imwrite("Img16BitGreen.png", Img);
    Img = Img.mul( cv::Scalar(2.2, 1.0, 1.4) );
    //imwrite("Img16MaybeColored.png", Img);
    vector<int> imwriteTags = {cv::IMWRITE_TIFF_COMPRESSION, 1};
    imwrite("Img16Colored.tiff", Img, imwriteTags);
    
    delete converter, convertedBuffer;
}
*/

bool JaiGo::SaveImage(const string path)
{

    //PvBufferWriter ImgWriter;
    //ImgWriter.GetConverter().SetBayerFilter(PvBayerFilterSimple);
    //PvBufferConverterRGBFilter ColorFilter;
    //ColorFilter.SetGainR(1.4f);
    //ColorFilter.SetGainG(1);
    //ColorFilter.SetGainB(3.4f);
    //ImgWriter.GetConverter().SetRGBFilter(ColorFilter);
    
    PvBuffer *lBuffer = NULL;
    PvResult lOperationResult;
    PvResult lPipelineResult = this->Pipeline->RetrieveNextBuffer( &lBuffer, 1000, &lOperationResult );
    
    PvPixelType goalPixelType;
    if (lBuffer->GetImage()->GetPixelType() == PvPixelBayerRG8)
    {
        goalPixelType = PvPixelBGR8;
    }
    else
    {
        goalPixelType = PvPixelBGR16;   
    }
    
    cout << "==============" << endl;
    if ( lPipelineResult.IsOK() && lOperationResult.IsOK() )
    {
        cout << "JAI: Saving image to " << path << endl;
        if (path.find("bmp") != string::npos)
        {
            cout << "JAI: Save .bmp TODO" << endl;
        }
        else if (path.find("tiff") != string::npos)
        {
            vector<int> imwriteTags = {cv::IMWRITE_TIFF_COMPRESSION, 1};
            imwrite(path.c_str(), JaiGo::GetCvImage(lBuffer, goalPixelType), imwriteTags);
        }
        else if (path.find("raw") != string::npos)
        {
            cout << "JAI: Save .raw TODO" << endl;
        }
    }

    cout << "==============" << endl;
    
    return true;
}

void JaiGo::CloseAndDisconnect()
{   
    if (this->StopCommand != NULL)
    {
        cout << "JAI: Sending AcquisitionStop command to the device" << endl;
        this->StopCommand->Execute();
    }

    if (this->Device != NULL)
    {
        // Disable streaming on the device
        cout << "JAI: Disable streaming on the controller." << endl;
        this->Device->StreamDisable();
    }

    if (this->Pipeline != NULL)
    {
        // Stop the pipeline
        cout << "JAI: Stop pipeline" << endl;
        this->Pipeline->Stop();

        cout << "JAI: Deleting pipeline" << endl;
        delete this->Pipeline;
    }

    if (this->Stream != NULL)
    {
        cout << "JAI: Closing stream" << endl;
        this->Stream->Close();
        PvStream::Free( this->Stream );
        //this->Streaming = false;
    }

    if (this->Device != NULL)
    {
        cout << "JAI: Disconnecting device" << endl;
        this->Device->Disconnect();
        PvDevice::Free( this->Device );
        this->Connected = false;
    }
}

bool JaiGo::SetPixelFormat(const string format)
{
    PvGenParameter *lParameter = this->DevParameters->Get( "PixelFormat" );
    PvGenEnum *lPixelFormatParameter = dynamic_cast<PvGenEnum *>( lParameter );
    
    if ( lPixelFormatParameter == NULL )
    {
        cout << "    JAI ERROR: Unable to get the pixel format parameter." << endl;
        return false;
    }

    PvResult lResult = lPixelFormatParameter->SetValue( format.c_str() );
    if ( lResult.IsFailure() )
    {
        cout << "   JAI ERROR: Error changing pixel format on device." << endl;
        cout << "   JAI ERROR: Supported input arguments are BayerRG8, BayerRG10, BayerRG10p, BayerRG12, and BayerRG12p." << endl;
        return false;
    }
    
    cout << "JAI: Changed pixel format to " << format << endl;
    return true;
}

py::dtype JaiGo::determine_np_dtype(int depth)
{
    switch (depth) {
    case CV_8U: return py::dtype::of<uint8_t>();
    case CV_8S: return py::dtype::of<int8_t>();
    case CV_16U: return py::dtype::of<uint16_t>();
    case CV_16S: return py::dtype::of<int16_t>();
    case CV_32S: return py::dtype::of<int32_t>();
    case CV_32F: return py::dtype::of<float>();
    case CV_64F: return py::dtype::of<double>();
    default:
        throw std::invalid_argument("Unsupported data type.");
    }
}

std::vector<std::size_t> JaiGo::determine_shape(cv::Mat& m)
{
    if (m.channels() == 1) {
        return {
            static_cast<size_t>(m.rows)
            , static_cast<size_t>(m.cols)
        };
    }

    return {
        static_cast<size_t>(m.rows)
        , static_cast<size_t>(m.cols)
        , static_cast<size_t>(m.channels())
    };
}

py::capsule JaiGo::make_capsule(cv::Mat& m)
{
    return py::capsule(new cv::Mat(m)
        , [](void *v) { delete reinterpret_cast<cv::Mat*>(v); }
        );
}

py::array JaiGo::mat_to_nparray(cv::Mat& m)
{
    if (!m.isContinuous()) {
        throw std::invalid_argument("Only continuous Mats supported.");
    }

    return py::array(determine_np_dtype(m.depth())
        , determine_shape(m)
        , m.data
        , make_capsule(m));
}

PYBIND11_MODULE(pyJaiGo, m) {
    m.doc() = "pybind11 Jai GO SDK module"; // optional module docstring

    py::class_<JaiGo>(m, "JaiGo")
        .def(py::init<>())
        .def("FindAndConnect", &JaiGo::FindAndConnect)
        .def("StartStream", &JaiGo::StartStream)
        .def("StopStream", &JaiGo::StopStream)
        .def("GrabImage", &JaiGo::GrabImage)
        .def("SaveImage", &JaiGo::SaveImage)
        .def("CloseAndDisconnect", &JaiGo::CloseAndDisconnect)

        .def("SetPixelFormat", &JaiGo::SetPixelFormat)

        .def_readwrite("Streaming", &JaiGo::Streaming)
        .def_readwrite("LoadCustomCameraConfiguration", &JaiGo::LoadCustomCameraConfiguration)
        .def_readwrite("CameraConfigurationPath", &JaiGo::CameraConfigurationPath)

        .def_readwrite("AdjustColors", &JaiGo::AdjustColors)
        .def_readwrite("GainB", &JaiGo::GainB)
        .def_readwrite("GainG", &JaiGo::GainG)
        .def_readwrite("GainR", &JaiGo::GainR)

        .def_readonly("Connected", &JaiGo::Connected)
        .def_readonly("FrameRate", &JaiGo::FrameRateVal)
        .def_readonly("BandWidth", &JaiGo::BandwidthVal)
        .def_readonly("ImgHeight", &JaiGo::ImgHeight)
        .def_readonly("ImgWidth", &JaiGo::ImgWidth)
        .def_readonly("Img", &JaiGo::npImg);
}
