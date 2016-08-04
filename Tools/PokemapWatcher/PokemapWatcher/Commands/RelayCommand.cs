using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace PokemapWatcher.Commands
{
    public class RelayCommand : ICommand
    {

        private Action<object> _action;

        /// <summary>Default Constructor</summary>
        /// <param name="action">Method, which will be called on <see cref="Execute(object)"/></param>
        public RelayCommand(Action<object> action)
        {
            _action = action;
        }

        #region ICommand
        /// <summary>See <see cref="ICommand"/></summary>
        public event EventHandler CanExecuteChanged;

        /// <summary>See <see cref="ICommand"/></summary>
        public bool CanExecute(object parameter)
        {
            return true;
        }

        /// <summary>See <see cref="ICommand"/></summary>
        public void Execute(object parameter)
        {
            if (parameter != null)
            {
                _action(parameter);
            }
            else
            {
                _action(null);
            }
        }
        #endregion
    }
}
