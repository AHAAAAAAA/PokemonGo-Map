using PokemapWatcher.Commands;
using PokemapWatcher.Model;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace PokemapWatcher.ViewModel
{
    public class MainViewVM : INotifyPropertyChanged
    {
        public MainViewVM()
        {
            InstanceList = new ObservableCollection<PokemapInstance>(SettingsProvider.readSettings());

            #region Commands
            CloseCommand = new RelayCommand(Close);

            SaveSettingsCommand = new RelayCommand(SaveSettings);


            CreateNewTabCommand = new RelayCommand(CreateNewTab);
            DeleteTabCommand = new RelayCommand(DeleteTab);

            NextTabCommand = new RelayCommand(NextTab);
            PrevTabCommand = new RelayCommand(PrevTab);


            StartProcCommand = new RelayCommand(StartProc);
            StopProcCommand = new RelayCommand(StopProc);

            StartProcAllCommand = new RelayCommand(StartProcAll);
            StopProcAllCommand = new RelayCommand(StopProcAll);
            #endregion
        }

        #region Commands
        private ICommand m_CloseCommand;
        public ICommand CloseCommand
        {
            get { return m_CloseCommand; }
            set
            {
                m_CloseCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void Close(object o)
        {
            StopProcAllCommand.Execute(null);
        }


        private ICommand m_SaveSettingsCommand;
        public ICommand SaveSettingsCommand
        {
            get { return m_SaveSettingsCommand; }
            set
            {
                m_SaveSettingsCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void SaveSettings (object o)
        {
            SettingsProvider.writeSettings(new List<PokemapInstance>(InstanceList));
        }




        private ICommand m_CreateNewTabCommand;
        public ICommand CreateNewTabCommand
        {
            get { return m_CreateNewTabCommand; }
            set
            {
                m_CreateNewTabCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void CreateNewTab(object o)
        {
            var i = new PokemapInstance();
            InstanceList.Add(i);
            SelectedInstance = i;
        }

        private ICommand m_DeleteTabCommand;
        public ICommand DeleteTabCommand
        {
            get { return m_DeleteTabCommand; }
            set
            {
                m_DeleteTabCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void DeleteTab(object o)
        {
            var i = SelectedInstance;
            SelectedInstance = null;
            InstanceList.Remove(i);
        }


        private ICommand m_NextTabCommand;
        public ICommand NextTabCommand
        {
            get { return m_NextTabCommand; }
            set
            {
                m_NextTabCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void NextTab(object o)
        {
            if (SelectedInstance != null)
            {
                var index = InstanceList.IndexOf(SelectedInstance);
                SelectedInstance = InstanceList[index + 1 >= InstanceList.Count ? 0 : index + 1];
            }
        }

        private ICommand m_PrevTabCommand;
        public ICommand PrevTabCommand
        {
            get { return m_PrevTabCommand; }
            set
            {
                m_PrevTabCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void PrevTab(object o)
        {
            if (SelectedInstance != null)
            {
                var index = InstanceList.IndexOf(SelectedInstance);
                SelectedInstance = InstanceList[index - 1 < 0 ? InstanceList.Count - 1 : index - 1];
            }
        }




        private ICommand m_StartProcCommand;
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
            SelectedInstance.Start();
        }

        private ICommand m_StopProcCommand;
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
            SelectedInstance.Stop();
        }


        private ICommand m_StartProcAllCommand;
        public ICommand StartProcAllCommand
        {
            get { return m_StartProcAllCommand; }
            set
            {
                m_StartProcAllCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void StartProcAll(object o)
        {
            foreach (PokemapInstance ins in InstanceList)
            {
                ins.Start();
            }
        }

        private ICommand m_StopProcAllCommand;
        public ICommand StopProcAllCommand
        {
            get { return m_StopProcAllCommand; }
            set
            {
                m_StopProcAllCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void StopProcAll(object o)
        {
            foreach (PokemapInstance ins in InstanceList)
            {
                ins.Stop();
            }
        }
        #endregion

        #region Member
        private ObservableCollection<PokemapInstance> m_InstanceList;        
        public ObservableCollection<PokemapInstance> InstanceList
        {
            get { return m_InstanceList; }
            set
            {
                m_InstanceList = value;
                NotifyPropertyChanged();
            }
        }

        private PokemapInstance m_SelectedInstance;
        public PokemapInstance SelectedInstance
        {
            get { return m_SelectedInstance; }
            set
            {
                m_SelectedInstance = value;
                NotifyPropertyChanged();
            }
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
