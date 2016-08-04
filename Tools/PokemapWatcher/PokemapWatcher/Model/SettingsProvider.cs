using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Serialization;

namespace PokemapWatcher.Model
{
    public static class SettingsProvider
    {
        #region Static Stuff
        public static string SETTINGS_FILE_PATH = @"C:\Users\Public\Documents\PkmnGoMapWatcher\";
        public static string SETTINGS_FILE_NAME = @"settings.xml";
        
        public static bool writeSettings(List<PokemapInstance> data)
        {
            TextWriter writer = null;
            try
            {
                // Serialize to Public Documents Directory
                if (!System.IO.Directory.Exists(SETTINGS_FILE_PATH))
                {
                    System.IO.Directory.CreateDirectory(SETTINGS_FILE_PATH);
                }
                XmlSerializer serializer = new XmlSerializer(typeof(List<PokemapInstance>));
                writer = new StreamWriter(SETTINGS_FILE_PATH + SETTINGS_FILE_NAME);
                serializer.Serialize(writer, data);
                writer.Close();
                return true;
            }
            catch (Exception ex)
            {
                if (writer != null) writer.Close();
                // Could not Serialize, Exception thrown as MsgBox
                //System.Windows.Forms.MessageBox.Show(ex.Message, "Settings couldn't be saved");
                return false;
            }
        }

        public static List<PokemapInstance> readSettings()
        {
            FileStream fs = null;
            try
            {
                // Deserialize XML File from Public Documents
                XmlSerializer serializer = new XmlSerializer(typeof(List<PokemapInstance>));
                fs = new FileStream(SETTINGS_FILE_PATH + SETTINGS_FILE_NAME, FileMode.Open);
                List<PokemapInstance> settings = (List<PokemapInstance>)serializer.Deserialize(fs);
                fs.Close();
                if (settings.Count == 0)
                    settings.Add(new PokemapInstance());
                return settings;
            }
            catch (Exception ex)
            {
                // If xml Settings could not be read, new SettingsProvider will be created with Basic Data;
                List<PokemapInstance> settings = new List<PokemapInstance>();
                if (fs != null) fs.Close();
                //System.Windows.Forms.MessageBox.Show(ex.Message, "Settings couldn't be loaded");
                return settings;
            }
        }
        #endregion
    }
}
