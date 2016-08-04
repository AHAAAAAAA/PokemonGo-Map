using PokemapWatcher.Commands;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Xml.Serialization;

namespace PokemapWatcher.Model
{
    public enum AuthService
    {
        none,
        ptc,
        google,
    }

    public class PokemapInstance : INotifyPropertyChanged
    {
        public PokemapInstance()
        {
            StartProcCommand = new RelayCommand(StartProc);
            StopProcCommand = new RelayCommand(StopProc);
        }

        #region Data
        #region Global
        [XmlIgnore]
        string m_InstanceName = "New Pokemon GO Map Instance";
        [XmlAttribute]
        public string InstanceName
        {
            get { return m_InstanceName; }
            set
            {
                m_InstanceName = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        bool m_Searcher = true;
        [XmlAttribute]
        public bool Searcher
        {
            get { return m_Searcher; }
            set
            {
                m_Searcher = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        bool m_Webserver = true;
        [XmlAttribute]
        public bool Webserver
        {
            get { return m_Webserver; }
            set
            {
                m_Webserver = value;
                NotifyPropertyChanged();
            }
        }
        #endregion

        #region Auth
        [XmlIgnore]
        AuthService m_AuthService = AuthService.ptc;
        [XmlAttribute]
        public AuthService AuthService
        {
            get { return m_AuthService; }
            set
            {
                m_AuthService = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        string m_Username = "";
        [XmlAttribute]
        public string Username
        {
            get { return m_Username; }
            set
            {
                m_Username = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        string m_Password = "";
        [XmlAttribute]
        public string Password
        {
            get { return m_Password; }
            set
            {
                m_Password = value;
                NotifyPropertyChanged();
            }
        }
        #endregion

        #region Location
        [XmlIgnore]
        string m_GoogleMapsKey = "put your gmaps-key here";
        [XmlAttribute]
        public string GoogleMapsKey
        {
            get { return m_GoogleMapsKey; }
            set
            {
                m_GoogleMapsKey = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        string m_Location = "latitude longitude";
        [XmlAttribute]
        public string Location
        {
            get { return m_Location; }
            set
            {
                m_Location = value;
                LocationHyperlink = "";
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        public string LocationHyperlink
        {
            get
            {
                var first = Location.Substring(0,Location.IndexOf(' '));
                var scnd = Location.Substring(Location.IndexOf(' ') + 1, Location.Length-(Location.IndexOf(' ') + 1));
                return "http://www.google.com/maps/place/" + first + "," + scnd;
            }
            set
            {
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        bool m_FixedLocation = true;
        [XmlAttribute]
        public bool FixedLocation
        {
            get { return m_FixedLocation; }
            set
            {
                m_FixedLocation = value;
                NotifyPropertyChanged();
            }
        }
        #endregion

        #region Server

        [XmlIgnore]
        string m_Host = "hostname";
        [XmlAttribute]
        public string Host
        {
            get { return m_Host; }
            set
            {
                m_Host = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        UInt16 m_Port = 8080;
        [XmlAttribute]
        public UInt16 Port
        {
            get { return m_Port; }
            set
            {
                m_Port = value;
                NotifyPropertyChanged();
            }
        }
        #endregion

        #region Searcher Settings
        [XmlIgnore]
        public UInt16 m_StepLimit = 5;
        [XmlAttribute]
        public UInt16 StepLimit
        {
            get { return m_StepLimit; }
            set
            {
                m_StepLimit = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        public UInt16 m_StepDelay = 5;
        [XmlAttribute]
        public UInt16 StepDelay
        {
            get { return m_StepDelay; }
            set
            {
                m_StepDelay = value;
                NotifyPropertyChanged();
            }
        }
        #endregion
        #endregion

        #region Member
        [XmlIgnore]
        private ObservableCollection<string> m_ProcOutput = new ObservableCollection<string>();
        [XmlIgnore]
        public ObservableCollection<string> ProcOutput
        {
            get { return m_ProcOutput; }
            set
            {
                m_ProcOutput = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        private bool m_Running = false;
        [XmlIgnore]
        public bool Running
        {
            get { return m_Running; }
            set
            {
                m_Running = value;
                NotifyPropertyChanged();
            }
        }
        [XmlIgnore]
        private bool m_NotRunning = true;
        [XmlIgnore]
        public bool NotRunning
        {
            get { return m_NotRunning; }
            set
            {
                m_NotRunning = value;
                NotifyPropertyChanged();
            }
        }
        
        [XmlIgnore]
        private Process Proc = null;
        #endregion

        #region Methods
        public void Start()
        {
            if (Proc == null)
            {
                Running = true;
                NotRunning = false;
                ProcOutput.Clear();
                ProcOutput.Add("Starting Instance");
                // Init Proc
                Proc = new Process();
                Proc.StartInfo.FileName = @"C:\Python27\python.exe";
                Proc.StartInfo.Arguments = BuildProcArguments();
                ProcOutput.Add("Run Pokemon GO Map Instance with args:");
                ProcOutput.Add(Proc.StartInfo.Arguments);
                ProcOutput.Add(" ");
                ProcOutput.Add("------------------");
                ProcOutput.Add(" ");
                Proc.StartInfo.UseShellExecute = false;
                Proc.StartInfo.RedirectStandardOutput = true;
                Proc.StartInfo.RedirectStandardError = true;
                Proc.StartInfo.CreateNoWindow = true;
                Proc.OutputDataReceived += Proc_OutputDataReceived;
                Proc.ErrorDataReceived += Proc_ErrorDataReceived;
                Proc.Exited += Proc_Exited;
                Proc.Start();
                Proc.BeginOutputReadLine();
                Proc.BeginErrorReadLine();
            }
        }
        
        private string BuildProcArguments()
        {
            string args = "runserver.py -L en ";

            // Google Maps Key
            args += "-k " + GoogleMapsKey + " ";
            // Location
            args += "-l \"" + Location + "\" ";
            // Searcher
            if (Searcher)
            {
                if (!Webserver)
                    args += "--no-server ";
                if (AuthService == AuthService.ptc)
                    args += "-a ptc ";
                else if (AuthService == AuthService.google)
                    args += "-a google ";
                if (AuthService != AuthService.none)
                {
                    // Username
                    args += "-u " + Username + " ";
                    // Password
                    args += "-p " + Password + " ";
                }
                // Step Limit
                args += "-st " + StepLimit + " ";
                // Step Delay
                args += "-sd " + StepDelay + " ";
            }
            // Webserver
            else if (Webserver)
            {
                if (!Searcher)
                    args += "--only-server ";
                // IP
                args += "-H " + Host + " ";
                // Port
                args += "-P " + Port + " ";
                // Fixed Location
                if (FixedLocation)
                    args += "-fl ";
            }

            return args;
        }
        public void Stop()
        {
            if (Proc != null)
            {
                Running = false;
                NotRunning = true;
                try
                {
                    Proc.Kill();
                }
                catch (Exception e)
                {
                    // Ignore
                }
                Proc = null;
            }
        }


        private void Proc_Exited(object sender, EventArgs e)
        {
            Stop();
        }

        private void Proc_OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (!String.IsNullOrEmpty(e.Data))
                Application.Current.Dispatcher.Invoke((Action)(() =>
                    {
                        ProcOutput.Add(e.Data);
                        while (ProcOutput.Count > 200)
                            ProcOutput.RemoveAt(0);
                    }));
        }

        private void Proc_ErrorDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (!String.IsNullOrEmpty(e.Data))
                Application.Current.Dispatcher.Invoke((Action)(() =>
                    {
                        ProcOutput.Add(e.Data);
                        while (ProcOutput.Count > 200)
                            ProcOutput.RemoveAt(0);
                    }));
        }
        #endregion

        #region Commands
        [XmlIgnore]
        private ICommand m_StartProcCommand;
        [XmlIgnore]
        public ICommand StartProcCommand
        {
            get { return m_StartProcCommand; }
            set
            {
                m_StartProcCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void StartProc(object o)
        {
            Start();
        }

        [XmlIgnore]
        private ICommand m_StopProcCommand;
        [XmlIgnore]
        public ICommand StopProcCommand
        {
            get { return m_StopProcCommand; }
            set
            {
                m_StopProcCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void StopProc(object o)
        {
            Stop();
        }
        #endregion

        #region INotifyPropertyChanged
        public event PropertyChangedEventHandler PropertyChanged;
        private void NotifyPropertyChanged([CallerMemberName] string PropertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(PropertyName));
        }
        #endregion
    }
}
