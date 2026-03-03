import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { t, translations } from './locales';

// API 基础URL，可以通过环境变量配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const [selectedChildData, setSelectedChildData] = useState(null);
  const [records, setRecords] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [showChildForm, setShowChildForm] = useState(false);
  const [showRecordForm, setShowRecordForm] = useState(false);
  const [editingChild, setEditingChild] = useState(null);
  const [editingRecord, setEditingRecord] = useState(null);
  const [lastRecordData, setLastRecordData] = useState(null);
  const [lastChildData, setLastChildData] = useState(null);
  const [activeTab, setActiveTab] = useState('records'); // 当前激活的标签页
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState(() => {
    // 从localStorage读取语言设置，默认为中文
    return localStorage.getItem('app_language') || 'zh';
  });
  
  // 翻译函数
  const translate = (key, params = {}) => t(key, language, params);

  // 当语言改变时，重新获取需要LLM生成的数据和用户输入的数据
  useEffect(() => {
    fetchChildren();  // 重新获取孩子列表以显示对应语言的内容
    if (selectedChild) {
      fetchChildData(selectedChild);  // 重新获取孩子数据以显示对应语言的内容
      fetchRecords(selectedChild);  // 重新获取记录以显示对应语言的内容
      fetchMilestones(selectedChild);
      fetchComparison(selectedChild);
    }
  }, [language]);  // 当语言改变时触发

  useEffect(() => {
    fetchChildren();
  }, []);

  useEffect(() => {
    if (selectedChild) {
      fetchChildData(selectedChild);
      fetchRecords(selectedChild);
      fetchMilestones(selectedChild);
      fetchComparison(selectedChild);
    }
  }, [selectedChild]);

  // 页面加载时，如果有选中的孩子，恢复选择状态
  useEffect(() => {
    const savedChildId = localStorage.getItem('selectedChildId');
    if (savedChildId && children.length > 0) {
      const childId = parseInt(savedChildId);
      if (children.some(c => c.id === childId)) {
        setSelectedChild(childId);
      }
    }
  }, [children]);

  // 保存选中的孩子ID到本地存储
  useEffect(() => {
    if (selectedChild) {
      localStorage.setItem('selectedChildId', selectedChild.toString());
    }
  }, [selectedChild]);

  const fetchChildData = async (childId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/children/${childId}`, {
        params: { language: language }
      });
      setSelectedChildData(response.data);
    } catch (error) {
      console.error('获取孩子信息失败:', error);
    }
  };

  const fetchComparison = async (childId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/children/${childId}/comparison`, {
        params: { language: language }
      });
      setComparison(response.data);
    } catch (error) {
      // 如果没有记录，这是正常的，不显示错误
      if (error.response?.status === 404) {
        setComparison(null);
      } else {
        console.error('获取对比信息失败:', error);
        setComparison({ error: '无法获取对比信息' });
      }
    }
  };

  const fetchChildren = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/children`);
      setChildren(response.data);
      // 保存最新的孩子信息，用于自动填充
      if (response.data && response.data.length > 0) {
        setLastChildData(response.data[response.data.length - 1]); // 获取最新的（最后一个）
      } else {
        setLastChildData(null);
      }
    } catch (error) {
      console.error('获取孩子列表失败:', error);
    }
  };

  const fetchRecords = async (childId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/children/${childId}/records`, {
        params: { language: language }
      });
      setRecords(response.data);
      // 保存最新记录数据，用于自动填充
      if (response.data && response.data.length > 0) {
        setLastRecordData(response.data[0]);
      } else {
        setLastRecordData(null);
      }
    } catch (error) {
      console.error('获取记录失败:', error);
    }
  };

  const fetchMilestones = async (childId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/children/${childId}/milestones`, {
        params: { language: language }
      });
      setMilestones(response.data);
    } catch (error) {
      console.error('获取里程碑失败:', error);
    }
  };

  const handleCreateChild = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData(e.target);
    
    try {
      const childData = new FormData();
      childData.append('name', formData.get('name'));
      childData.append('birth_date', formData.get('birth_date'));
      childData.append('special_conditions', formData.get('special_conditions'));
      childData.append('gender', formData.get('gender') || '');
      childData.append('request_language', language);
      
      await axios.post(`${API_BASE_URL}/api/children`, childData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setShowChildForm(false);
      fetchChildren();
      alert(translate('profile.createSuccess'));
    } catch (error) {
      alert(translate('profile.createFailed') + ': ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRecord = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData(e.target);
    
    try {
      const recordData = new FormData();
      recordData.append('child_id', selectedChild);
      recordData.append('height', formData.get('height') || '');
      recordData.append('weight', formData.get('weight') || '');
      recordData.append('head_circumference', formData.get('head_circumference') || '');
      recordData.append('gross_motor', formData.get('gross_motor') || '');
      recordData.append('language', formData.get('language') || '');  // 孩子的语言发展情况
      recordData.append('fine_motor', formData.get('fine_motor') || '');
      recordData.append('sleep', formData.get('sleep') || '');
      recordData.append('diet', formData.get('diet') || '');
      recordData.append('notes', formData.get('notes') || '');
      recordData.append('request_language', language);  // 传递当前界面语言，用于LLM生成

              const imageFiles = formData.getAll('images');
      imageFiles.forEach(file => {
        if (file && file.size > 0) {
          recordData.append('images', file);
        }
      });

      const videoFiles = formData.getAll('videos');
      videoFiles.forEach(file => {
        if (file && file.size > 0) {
          recordData.append('videos', file);
        }
      });

      await axios.post(`${API_BASE_URL}/api/records`, recordData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setShowRecordForm(false);
      // 刷新记录列表，并自动保存最新记录用于下次填充
      await fetchRecords(selectedChild);
      fetchMilestones(selectedChild);
      fetchComparison(selectedChild);
      alert(translate('records.createSuccess'));
    } catch (error) {
      alert(translate('records.createFailed') + ': ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateChild = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData(e.target);
    
    try {
      const updateData = new FormData();
      updateData.append('name', formData.get('name'));
      updateData.append('birth_date', formData.get('birth_date'));
      updateData.append('special_conditions', formData.get('special_conditions'));
      updateData.append('gender', formData.get('gender') || '');
      updateData.append('request_language', language);
      
      await axios.put(`${API_BASE_URL}/api/children/${editingChild.id}`, updateData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setEditingChild(null);
      fetchChildren();
      if (selectedChild === editingChild.id) {
        fetchChildData(editingChild.id);
        fetchComparison(editingChild.id);
      }
      alert(translate('profile.updateSuccess'));
    } catch (error) {
      alert(translate('profile.updateFailed') + ': ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRecord = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData(e.target);
    
    try {
      const recordData = new FormData();
      recordData.append('child_id', selectedChild);
      recordData.append('height', formData.get('height') || '');
      recordData.append('weight', formData.get('weight') || '');
      recordData.append('head_circumference', formData.get('head_circumference') || '');
      recordData.append('gross_motor', formData.get('gross_motor') || '');
      recordData.append('language', formData.get('language') || '');
      recordData.append('fine_motor', formData.get('fine_motor') || '');
      recordData.append('sleep', formData.get('sleep') || '');
      recordData.append('diet', formData.get('diet') || '');
      recordData.append('notes', formData.get('notes') || '');
      recordData.append('request_language', language);  // 传递当前界面语言

      await axios.put(`${API_BASE_URL}/api/records/${editingRecord.id}`, recordData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setEditingRecord(null);
      fetchRecords(selectedChild);
      fetchMilestones(selectedChild);
      fetchComparison(selectedChild);
      alert(translate('records.updateSuccess'));
    } catch (error) {
      alert(translate('records.updateFailed') + ': ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm(translate('records.deleteConfirm'))) {
      return;
    }
    
    setLoading(true);
    try {
      await axios.delete(`${API_BASE_URL}/api/records/${recordId}`);
      
      // 关闭编辑表单（如果正在编辑被删除的记录）
      if (editingRecord && editingRecord.id === recordId) {
        setEditingRecord(null);
      }
      
      // 删除成功后，刷新数据
      await fetchRecords(selectedChild);
      
      // 检查是否还有记录，然后决定是否获取里程碑和对比
      try {
        const updatedRecords = await axios.get(`${API_BASE_URL}/api/children/${selectedChild}/records`);
        if (updatedRecords.data && updatedRecords.data.length > 0) {
          // 如果还有记录，获取里程碑和对比（使用 Promise.allSettled 避免单个失败影响整体）
          await Promise.allSettled([
            fetchMilestones(selectedChild),
            fetchComparison(selectedChild)
          ]);
        } else {
          // 如果没有记录了，清空里程碑和对比
          setMilestones([]);
          setComparison(null);
        }
      } catch (err) {
        console.error('刷新数据失败:', err);
        // 即使刷新失败，也清空可能无效的数据
        setMilestones([]);
        setComparison(null);
      }
      
      // 延迟显示成功消息，避免阻塞UI更新
      setTimeout(() => {
        alert('记录删除成功！');
      }, 100);
    } catch (error) {
      console.error('删除失败:', error);
      alert(translate('records.deleteFailed') + ': ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const getStatusClass = (status) => {
    if (!status) return '';
    if (status.includes('正常')) return 'status-normal';
    if (status.includes('良性')) return 'status-good';
    if (status.includes('倒退')) return 'status-regression';
    return '';
  };

  // 切换语言
  const toggleLanguage = () => {
    const newLang = language === 'zh' ? 'en' : 'zh';
    setLanguage(newLang);
    localStorage.setItem('app_language', newLang);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>{translate('app.title')}</h1>
        <button 
          className="language-toggle"
          onClick={toggleLanguage}
          title={language === 'zh' ? 'Switch to English' : '切换到中文'}
        >
          {language === 'zh' ? 'EN' : '中文'}
        </button>
      </header>

      <div className="container">
        {/* 顶部导航菜单 - 放在标题下方 */}
        {selectedChild && (
          <div className="card" style={{ marginBottom: '20px', padding: '0' }}>
            <div style={{ display: 'flex', borderBottom: '2px solid #e0e0e0' }}>
              <button
                onClick={() => setActiveTab('profile')}
                style={{
                  flex: 1,
                  padding: '16px 20px',
                  border: 'none',
                  backgroundColor: activeTab === 'profile' ? '#007bff' : 'transparent',
                  color: activeTab === 'profile' ? 'white' : '#666',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: activeTab === 'profile' ? 'bold' : 'normal',
                  transition: 'all 0.3s',
                  borderBottom: activeTab === 'profile' ? '3px solid #0056b3' : '3px solid transparent'
                }}
                >
                  👤 {translate('menu.profile')}
                </button>
                <button
                  onClick={() => setActiveTab('records')}
                  style={{
                    flex: 1,
                    padding: '16px 20px',
                    border: 'none',
                    backgroundColor: activeTab === 'records' ? '#007bff' : 'transparent',
                    color: activeTab === 'records' ? 'white' : '#666',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: activeTab === 'records' ? 'bold' : 'normal',
                    transition: 'all 0.3s',
                    borderBottom: activeTab === 'records' ? '3px solid #0056b3' : '3px solid transparent'
                  }}
                >
                  📝 {translate('menu.records')}
                </button>
                <button
                  onClick={() => setActiveTab('comparison')}
                  style={{
                    flex: 1,
                    padding: '16px 20px',
                    border: 'none',
                    backgroundColor: activeTab === 'comparison' ? '#007bff' : 'transparent',
                    color: activeTab === 'comparison' ? 'white' : '#666',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: activeTab === 'comparison' ? 'bold' : 'normal',
                    transition: 'all 0.3s',
                    borderBottom: activeTab === 'comparison' ? '3px solid #0056b3' : '3px solid transparent'
                  }}
                >
                  📊 {translate('menu.comparison')}
                </button>
                <button
                  onClick={() => setActiveTab('milestones')}
                  style={{
                    flex: 1,
                    padding: '16px 20px',
                    border: 'none',
                    backgroundColor: activeTab === 'milestones' ? '#007bff' : 'transparent',
                    color: activeTab === 'milestones' ? 'white' : '#666',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: activeTab === 'milestones' ? 'bold' : 'normal',
                    transition: 'all 0.3s',
                    borderBottom: activeTab === 'milestones' ? '3px solid #0056b3' : '3px solid transparent'
                  }}
                >
                  🎯 {translate('menu.milestones')}
                </button>
            </div>
          </div>
        )}


        {/* 孩子档案 - 无论是否选择孩子都显示 */}
        {activeTab === 'profile' && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2>{translate('profile.title')}</h2>
              <div>
                {!selectedChild && (
                  <button className="btn btn-primary" onClick={() => setShowChildForm(!showChildForm)}>
                    {showChildForm ? translate('common.cancel') : '+ ' + translate('profile.create')}
                  </button>
                )}
                {selectedChild && selectedChildData && (
                  <button 
                    className="btn btn-secondary" 
                    onClick={() => setEditingChild(selectedChildData)}
                    style={{ fontSize: '14px', padding: '8px 16px' }}
                  >
                    ✏️ {translate('profile.edit')}
                  </button>
                )}
              </div>
            </div>

            {/* 编辑孩子档案表单 */}
            {editingChild && (
              <form onSubmit={handleUpdateChild} className="card" style={{ marginTop: '20px', backgroundColor: '#fff3cd' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3>{translate('profile.editTitle')}</h3>
                  <button type="button" className="btn btn-secondary" onClick={() => setEditingChild(null)}>
                    {translate('common.cancel')}
                  </button>
                </div>
                <div className="form-group">
                  <label>{translate('profile.name')} *</label>
                  <input 
                    type="text" 
                    name="name" 
                    defaultValue={editingChild.name || ''} 
                    required 
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>{translate('profile.birthDate')} *</label>
                    <input 
                      type="date" 
                      name="birth_date" 
                      defaultValue={editingChild.birth_date || ''} 
                      required 
                    />
                  </div>
                  <div className="form-group">
                    <label>{translate('profile.gender')}</label>
                    <select name="gender" defaultValue={editingChild.gender || ''}>
                      <option value="">{translate('profile.selectGender')}</option>
                      <option value="男">{translate('profile.male')}</option>
                      <option value="女">{translate('profile.female')}</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label>{translate('profile.specialConditions')} *</label>
                  <textarea 
                    name="special_conditions" 
                    defaultValue={editingChild.special_conditions || ''} 
                    placeholder={translate('profile.specialConditionsPlaceholder')} 
                    required 
                  />
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? translate('common.loading') : translate('common.save')}
                </button>
              </form>
            )}

            {/* 创建孩子档案表单 */}
            {showChildForm && !editingChild && (
              <form onSubmit={handleCreateChild} className="card" style={{ marginTop: '20px', backgroundColor: '#f8f9fa' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3>创建孩子档案</h3>
                  {lastChildData && (
                    <span style={{ fontSize: '12px', color: '#666', fontStyle: 'italic' }}>
                      💡 已自动填充上次档案信息，可直接修改
                    </span>
                  )}
                </div>
                <div className="form-group">
                  <label>{translate('profile.name')} *</label>
                  <input 
                    type="text" 
                    name="name" 
                    defaultValue={lastChildData?.name || ''} 
                    placeholder={lastChildData?.name ? `上次: ${lastChildData.name}` : ''}
                    required 
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>{translate('profile.birthDate')} *</label>
                    <input 
                      type="date" 
                      name="birth_date" 
                      defaultValue={lastChildData?.birth_date || ''} 
                      required 
                    />
                  </div>
                  <div className="form-group">
                    <label>{translate('profile.gender')}</label>
                    <select name="gender" defaultValue={lastChildData?.gender || ''}>
                      <option value="">{translate('profile.selectGender')}</option>
                      <option value="男">{translate('profile.male')}</option>
                      <option value="女">{translate('profile.female')}</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label>{translate('profile.specialConditions')} *</label>
                  <textarea 
                    name="special_conditions" 
                    defaultValue={lastChildData?.special_conditions || ''} 
                    placeholder={lastChildData?.special_conditions ? `上次记录: ${lastChildData.special_conditions.substring(0, 100)}...` : translate('profile.specialConditionsPlaceholder')} 
                    required 
                  />
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? translate('common.loading') : translate('profile.create')}
                </button>
              </form>
            )}

            {/* 显示已选择的孩子档案 */}
            {selectedChildData && !editingChild && (
              <div style={{ marginTop: '20px' }}>
                <div className="form-row">
                  <p><strong>{translate('profile.name')}:</strong> {selectedChildData.name}</p>
                  <p><strong>{translate('profile.birthDate')}:</strong> {selectedChildData.birth_date}</p>
                  <p><strong>{translate('profile.gender')}:</strong> {selectedChildData.gender || translate('profile.notFilled')}</p>
                </div>
                <div style={{ marginTop: '12px' }}>
                  <strong>{translate('profile.specialConditions')}:</strong>
                  <p style={{ whiteSpace: 'pre-wrap', marginTop: '4px' }}>{selectedChildData.special_conditions}</p>
                </div>
                <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #ddd' }}>
                  <button 
                    className="btn btn-secondary" 
                    onClick={() => setEditingChild(selectedChildData)}
                    style={{ fontSize: '14px', padding: '8px 16px' }}
                  >
                    ✏️ {translate('profile.edit')}
                  </button>
                </div>
              </div>
            )}

            {/* 如果没有选择孩子且没有显示创建表单，显示提示 */}
            {!selectedChild && !showChildForm && (
              <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
                <p style={{ fontSize: '16px', marginBottom: '8px' }}>{translate('profile.pleaseCreate')}</p>
                <p style={{ fontSize: '14px' }}>{translate('profile.clickToCreate')}</p>
              </div>
            )}
          </div>
        )}

        {selectedChild && (
          <>

            {/* 发育记录 */}
            {activeTab === 'records' && (
              <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                  <h2>{translate('records.title')}</h2>
                  {records.length > 0 && (
                    <p style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
                      {translate('records.total', { count: records.length })}
                    </p>
                  )}
                </div>
                <button className="btn btn-primary" onClick={() => setShowRecordForm(!showRecordForm)}>
                  {showRecordForm ? translate('common.cancel') : '+ ' + translate('records.create')}
                </button>
              </div>

              {editingRecord && (
                <form onSubmit={handleUpdateRecord} className="card" style={{ marginTop: '20px', backgroundColor: '#fff3cd' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3>{translate('records.editTitle')}</h3>
                    <button type="button" className="btn btn-secondary" onClick={() => setEditingRecord(null)}>
                      {translate('common.cancel')}
                    </button>
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>{translate('records.height')} (cm)</label>
                      <input type="number" step="0.1" name="height" defaultValue={editingRecord.height || ''} />
                    </div>
                    <div className="form-group">
                      <label>{translate('records.weight')} (kg)</label>
                      <input type="number" step="0.1" name="weight" defaultValue={editingRecord.weight || ''} />
                    </div>
                    <div className="form-group">
                      <label>{translate('records.headCircumference')} (cm)</label>
                      <input type="number" step="0.1" name="head_circumference" defaultValue={editingRecord.head_circumference || ''} />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>{translate('records.grossMotor')}</label>
                    <textarea name="gross_motor" defaultValue={editingRecord.gross_motor || ''} placeholder={translate('records.grossMotorPlaceholder')} />
                  </div>

                  <div className="form-group">
                    <label>{translate('records.language')}</label>
                    <textarea name="language" defaultValue={editingRecord.language || ''} placeholder={translate('records.languagePlaceholder')} />
                  </div>

                  <div className="form-group">
                    <label>{translate('records.fineMotor')}</label>
                    <textarea name="fine_motor" defaultValue={editingRecord.fine_motor || ''} placeholder={translate('records.fineMotorPlaceholder')} />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>{translate('records.sleep')}</label>
                      <textarea name="sleep" defaultValue={editingRecord.sleep || ''} placeholder={translate('records.sleepPlaceholder')} />
                    </div>
                    <div className="form-group">
                      <label>{translate('records.diet')}</label>
                      <textarea name="diet" defaultValue={editingRecord.diet || ''} placeholder={translate('records.dietPlaceholder')} />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>{translate('records.notes')}</label>
                    <textarea name="notes" defaultValue={editingRecord.notes || ''} placeholder={translate('records.notesPlaceholder')} />
                  </div>

                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? translate('common.loading') : translate('common.save')}
                  </button>
                </form>
              )}

              {showRecordForm && (
                <form onSubmit={handleCreateRecord} className="card" style={{ marginTop: '20px', backgroundColor: '#f8f9fa' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3>{translate('records.createTitle')}</h3>
                    {lastRecordData && (
                      <span style={{ fontSize: '12px', color: '#666', fontStyle: 'italic' }}>
                        💡 {translate('records.autoFill')}
                      </span>
                    )}
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>{translate('records.height')} (cm)</label>
                      <input 
                        type="number" 
                        step="0.1" 
                        name="height" 
                        defaultValue={lastRecordData?.height || ''} 
                        placeholder={lastRecordData?.height ? `上次: ${lastRecordData.height}` : ''}
                      />
                    </div>
                    <div className="form-group">
                      <label>{translate('records.weight')} (kg)</label>
                      <input 
                        type="number" 
                        step="0.1" 
                        name="weight" 
                        defaultValue={lastRecordData?.weight || ''} 
                        placeholder={lastRecordData?.weight ? `上次: ${lastRecordData.weight}` : ''}
                      />
                    </div>
                    <div className="form-group">
                      <label>{translate('records.headCircumference')} (cm)</label>
                      <input 
                        type="number" 
                        step="0.1" 
                        name="head_circumference" 
                        defaultValue={lastRecordData?.head_circumference || ''} 
                        placeholder={lastRecordData?.head_circumference ? `上次: ${lastRecordData.head_circumference}` : ''}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>{translate('records.grossMotor')}</label>
                    <textarea 
                      name="gross_motor" 
                      defaultValue={lastRecordData?.gross_motor || ''} 
                      placeholder={lastRecordData?.gross_motor ? `上次记录: ${lastRecordData.gross_motor.substring(0, 50)}...` : translate('records.grossMotorPlaceholder')} 
                    />
                  </div>

                  <div className="form-group">
                    <label>{translate('records.language')}</label>
                    <textarea 
                      name="language" 
                      defaultValue={lastRecordData?.language || ''} 
                      placeholder={lastRecordData?.language ? `上次记录: ${lastRecordData.language.substring(0, 50)}...` : translate('records.languagePlaceholder')} 
                    />
                  </div>

                  <div className="form-group">
                    <label>{translate('records.fineMotor')}</label>
                    <textarea 
                      name="fine_motor" 
                      defaultValue={lastRecordData?.fine_motor || ''} 
                      placeholder={lastRecordData?.fine_motor ? `上次记录: ${lastRecordData.fine_motor.substring(0, 50)}...` : translate('records.fineMotorPlaceholder')} 
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>{translate('records.sleep')}</label>
                      <textarea 
                        name="sleep" 
                        defaultValue={lastRecordData?.sleep || ''} 
                        placeholder={lastRecordData?.sleep ? `上次记录: ${lastRecordData.sleep.substring(0, 50)}...` : translate('records.sleepPlaceholder')} 
                      />
                    </div>
                    <div className="form-group">
                      <label>{translate('records.diet')}</label>
                      <textarea 
                        name="diet" 
                        defaultValue={lastRecordData?.diet || ''} 
                        placeholder={lastRecordData?.diet ? `上次记录: ${lastRecordData.diet.substring(0, 50)}...` : translate('records.dietPlaceholder')} 
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>{translate('records.notes')}</label>
                    <textarea 
                      name="notes" 
                      defaultValue={lastRecordData?.notes || ''} 
                      placeholder={lastRecordData?.notes ? `上次记录: ${lastRecordData.notes.substring(0, 50)}...` : translate('records.notesPlaceholder')} 
                    />
                  </div>

                  <div className="form-group">
                    <label>{translate('records.uploadImages')}</label>
                    <input type="file" name="images" multiple accept="image/*" />
                  </div>

                  <div className="form-group">
                    <label>{translate('records.uploadVideos')}</label>
                    <input type="file" name="videos" multiple accept="video/*" />
                  </div>

                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? translate('common.loading') : translate('common.submit')}
                  </button>
                </form>
              )}

              <div style={{ marginTop: '20px' }}>
                {records.length === 0 ? (
                  <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
                    <p style={{ fontSize: '16px', marginBottom: '8px' }}>{translate('records.noRecords')}</p>
                    <p style={{ fontSize: '14px' }}>{translate('records.clickToCreate')}</p>
                  </div>
                ) : (
                  records.map(record => (
                    <div key={record.id} className="card" style={{ marginBottom: '16px', border: '1px solid #007bff', borderLeft: '4px solid #007bff' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                        <div>
                          <h4 style={{ color: '#007bff', marginBottom: '4px' }}>
                            {translate('records.recordDate')}: {new Date(record.record_date).toLocaleDateString(language === 'zh' ? 'zh-CN' : 'en-US')}
                          </h4>
                          <p style={{ fontSize: '12px', color: '#999' }}>
                            {new Date(record.record_date).toLocaleTimeString(language === 'zh' ? 'zh-CN' : 'en-US', { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                        {record.assessment && (
                          <span className={`status-badge ${getStatusClass(record.assessment)}`}>
                            {record.assessment}
                          </span>
                        )}
                      </div>

                    <div className="form-row">
                      {record.height && <p><strong>{translate('records.height')}:</strong> {record.height} cm</p>}
                      {record.weight && <p><strong>{translate('records.weight')}:</strong> {record.weight} kg</p>}
                      {record.head_circumference && <p><strong>{translate('records.headCircumference')}:</strong> {record.head_circumference} cm</p>}
                    </div>

                    <div style={{ marginTop: '12px' }}>
                      <strong>{translate('records.grossMotor')}:</strong> 
                      <p style={{ whiteSpace: 'pre-wrap', marginTop: '4px' }}>
                        {record.gross_motor || translate('records.notFilled')}
                      </p>
                    </div>

                    <div style={{ marginTop: '12px' }}>
                      <strong>{translate('records.language')}:</strong> 
                      <p style={{ whiteSpace: 'pre-wrap', marginTop: '4px' }}>
                        {record.language || translate('records.notFilled')}
                      </p>
                    </div>

                    <div style={{ marginTop: '12px' }}>
                      <strong>{translate('records.fineMotor')}:</strong> 
                      <p style={{ whiteSpace: 'pre-wrap', marginTop: '4px' }}>
                        {record.fine_motor || translate('records.notFilled')}
                      </p>
                    </div>

                    {(record.sleep || record.diet) && (
                      <div className="form-row" style={{ marginTop: '12px' }}>
                        {record.sleep && (
                          <div>
                            <strong>{translate('records.sleep')}:</strong> 
                            <p style={{ whiteSpace: 'pre-wrap', marginTop: '4px' }}>{record.sleep}</p>
                          </div>
                        )}
                        {record.diet && (
                          <div>
                            <strong>{translate('records.diet')}:</strong> 
                            <p style={{ whiteSpace: 'pre-wrap', marginTop: '4px' }}>{record.diet}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {record.notes && (
                      <div style={{ marginTop: '12px' }}>
                        <strong>{translate('records.notes')}:</strong> 
                        <p style={{ whiteSpace: 'pre-wrap', marginTop: '4px' }}>{record.notes}</p>
                      </div>
                    )}

                    {record.assessment_details && (
                      <div style={{ marginTop: '12px' }}>
                        {typeof record.assessment_details === 'object' ? (
                          <>
                            {/* 新的结构化显示 */}
                            <div style={{ padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px', marginBottom: '12px' }}>
                              <h5 style={{ marginBottom: '12px', color: '#007bff' }}>📊 {translate('records.assessmentSummary')}</h5>
                              {record.assessment_details.summary && (
                                <p style={{ marginBottom: '12px', fontWeight: '500' }}>{record.assessment_details.summary}</p>
                              )}
                              {record.assessment_details.details && (
                                <p style={{ whiteSpace: 'pre-wrap', color: '#666' }}>{record.assessment_details.details}</p>
                              )}
                            </div>

                            {record.assessment_details.evidence && (
                              <div style={{ padding: '16px', backgroundColor: '#e7f3ff', borderRadius: '4px', marginBottom: '12px' }}>
                                <h5 style={{ marginBottom: '12px', color: '#0056b3' }}>🔍 {translate('records.assessmentEvidence')}</h5>
                                
                                {record.assessment_details.evidence.data_comparison && (
                                  <div style={{ marginBottom: '12px' }}>
                                    <strong>📈 {translate('records.dataComparison')}：</strong>
                                    <p style={{ marginTop: '4px', marginLeft: '20px', color: '#333' }}>
                                      {record.assessment_details.evidence.data_comparison}
                                    </p>
                                  </div>
                                )}

                                {record.assessment_details.evidence.standard_reference && (
                                  <div style={{ marginBottom: '12px' }}>
                                    <strong>📚 {translate('records.standardReference')}：</strong>
                                    <p style={{ marginTop: '4px', marginLeft: '20px', color: '#333' }}>
                                      {record.assessment_details.evidence.standard_reference}
                                    </p>
                                  </div>
                                )}

                                {record.assessment_details.evidence.key_indicators && record.assessment_details.evidence.key_indicators.length > 0 && (
                                  <div style={{ marginBottom: '12px' }}>
                                    <strong>🎯 {translate('records.keyIndicators')}：</strong>
                                    <ul style={{ marginTop: '4px', marginLeft: '20px', color: '#333' }}>
                                      {record.assessment_details.evidence.key_indicators.map((indicator, idx) => (
                                        <li key={idx}>{indicator}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {record.assessment_details.evidence.trend_analysis && (
                                  <div style={{ marginBottom: '12px' }}>
                                    <strong>📉 {translate('records.trendAnalysis')}：</strong>
                                    <p style={{ marginTop: '4px', marginLeft: '20px', color: '#333' }}>
                                      {record.assessment_details.evidence.trend_analysis}
                                    </p>
                                  </div>
                                )}
                              </div>
                            )}

                            {record.assessment_details.concerns && record.assessment_details.concerns.length > 0 && (
                              <div style={{ padding: '16px', backgroundColor: '#fff3cd', borderRadius: '4px', marginBottom: '12px' }}>
                                <h5 style={{ marginBottom: '12px', color: '#856404' }}>⚠️ {translate('records.concerns')}</h5>
                                <ul style={{ marginLeft: '20px', color: '#856404' }}>
                                  {record.assessment_details.concerns.map((concern, idx) => (
                                    <li key={idx}>{concern}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {record.assessment_details.recommendations && record.assessment_details.recommendations.length > 0 && (
                              <div style={{ padding: '16px', backgroundColor: '#d1ecf1', borderRadius: '4px' }}>
                                <h5 style={{ marginBottom: '12px', color: '#0c5460' }}>💡 {translate('records.recommendations')}</h5>
                                <ul style={{ marginLeft: '20px', color: '#0c5460' }}>
                                  {record.assessment_details.recommendations.map((rec, idx) => (
                                    <li key={idx}>{rec}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </>
                        ) : (
                          /* 兼容旧格式 */
                          <div style={{ padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                            <strong>{translate('records.assessment')}:</strong>
                            <p style={{ marginTop: '8px', whiteSpace: 'pre-wrap' }}>{record.assessment_details}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {record.image_paths && record.image_paths.length > 0 && (
                      <div style={{ marginTop: '12px' }}>
                        <strong>{translate('records.images')}:</strong>
                        <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
                          {record.image_paths.map((path, idx) => (
                            <img
                              key={idx}
                              src={`${API_BASE_URL}/${path}`}
                              alt={`记录图片 ${idx + 1}`}
                              style={{ maxWidth: '200px', maxHeight: '200px', borderRadius: '4px' }}
                            />
                          ))}
                        </div>
                      </div>
                    )}

                    <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #ddd', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '12px', color: '#666' }}>
                        💡 可编辑或删除此记录
                      </span>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button 
                          className="btn btn-primary" 
                          onClick={() => {
                            setEditingRecord(record);
                            setShowRecordForm(false); // 关闭新建表单（如果有打开）
                            // 滚动到编辑表单
                            setTimeout(() => {
                              document.querySelector('form[onSubmit]')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }, 100);
                          }}
                          style={{ fontSize: '14px', padding: '8px 16px' }}
                        >
                          ✏️ 编辑
                        </button>
                        <button 
                          className="btn btn-secondary" 
                          onClick={() => handleDeleteRecord(record.id)}
                          style={{ fontSize: '14px', padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none' }}
                          disabled={loading}
                        >
                          🗑️ 删除
                        </button>
                      </div>
                    </div>
                  </div>
                  ))
                )}
              </div>
            </div>
            )}

            {/* 正常发育标准对比 */}
            {activeTab === 'comparison' && (
              <div className="card">
                <h2>📊 {translate('comparison.title')}</h2>
                {!comparison ? (
                  <p style={{ color: '#666', marginTop: '20px', padding: '40px', textAlign: 'center' }}>
                    {translate('comparison.noData')}
                  </p>
                ) : comparison.error ? (
                  <p style={{ color: '#666', marginTop: '20px' }}>{translate('comparison.error')}</p>
                ) : (
                  <div style={{ marginTop: '20px' }}>
                    <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: '#e7f3ff', borderRadius: '4px' }}>
                      <h3 style={{ color: '#0056b3', marginBottom: '12px' }}>{translate('comparison.currentAge')}：{comparison.age_months} {translate('comparison.months')}</h3>
                    </div>

                    {comparison.normal_standards && (
                      <div style={{ marginBottom: '24px' }}>
                        <h3 style={{ marginBottom: '16px', color: '#007bff' }}>✅ {translate('comparison.normalAbilities')}</h3>
                        
                        {comparison.normal_standards.physical && (
                          <div style={{ marginBottom: '16px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                            <h4 style={{ marginBottom: '8px' }}>{translate('comparison.physicalIndicators')}：</h4>
                            <ul style={{ marginLeft: '20px' }}>
                              {comparison.normal_standards.physical.height_range && (
                                <li>{translate('comparison.heightRange')}：{comparison.normal_standards.physical.height_range}</li>
                              )}
                              {comparison.normal_standards.physical.weight_range && (
                                <li>{translate('comparison.weightRange')}：{comparison.normal_standards.physical.weight_range}</li>
                              )}
                              {comparison.normal_standards.physical.head_circumference_range && (
                                <li>{translate('comparison.headCircumferenceRange')}：{comparison.normal_standards.physical.head_circumference_range}</li>
                              )}
                            </ul>
                          </div>
                        )}

                        {comparison.normal_standards.gross_motor && comparison.normal_standards.gross_motor.length > 0 && (
                          <div style={{ marginBottom: '16px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                            <h4 style={{ marginBottom: '8px' }}>{translate('comparison.grossMotorAbilities')}：</h4>
                            <ul style={{ marginLeft: '20px' }}>
                              {comparison.normal_standards.gross_motor.map((ability, idx) => (
                                <li key={idx}>{ability}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {comparison.normal_standards.language && comparison.normal_standards.language.length > 0 && (
                          <div style={{ marginBottom: '16px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                            <h4 style={{ marginBottom: '8px' }}>{translate('comparison.languageAbilities')}：</h4>
                            <ul style={{ marginLeft: '20px' }}>
                              {comparison.normal_standards.language.map((ability, idx) => (
                                <li key={idx}>{ability}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {comparison.normal_standards.fine_motor && comparison.normal_standards.fine_motor.length > 0 && (
                          <div style={{ marginBottom: '16px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                            <h4 style={{ marginBottom: '8px' }}>{translate('comparison.fineMotorAbilities')}：</h4>
                            <ul style={{ marginLeft: '20px' }}>
                              {comparison.normal_standards.fine_motor.map((ability, idx) => (
                                <li key={idx}>{ability}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {comparison.normal_standards.cognitive && comparison.normal_standards.cognitive.length > 0 && (
                          <div style={{ marginBottom: '16px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                            <h4 style={{ marginBottom: '8px' }}>{translate('comparison.cognitiveAbilities')}：</h4>
                            <ul style={{ marginLeft: '20px' }}>
                              {comparison.normal_standards.cognitive.map((ability, idx) => (
                                <li key={idx}>{ability}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {comparison.comparison && (
                      <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: '#fff3cd', borderRadius: '4px' }}>
                        <h3 style={{ marginBottom: '16px', color: '#856404' }}>📉 {translate('comparison.comparisonAnalysis')}</h3>
                        
                        {comparison.comparison.physical_comparison && (
                          <div style={{ marginBottom: '12px' }}>
                            <strong>{translate('comparison.physicalComparison')}：</strong>
                            <p style={{ marginTop: '4px', marginLeft: '20px', whiteSpace: 'pre-wrap' }}>
                              {comparison.comparison.physical_comparison}
                            </p>
                          </div>
                        )}

                        {comparison.comparison.gross_motor_comparison && (
                          <div style={{ marginBottom: '12px' }}>
                            <strong>{translate('comparison.grossMotorComparison')}：</strong>
                            <p style={{ marginTop: '4px', marginLeft: '20px', whiteSpace: 'pre-wrap' }}>
                              {comparison.comparison.gross_motor_comparison}
                            </p>
                          </div>
                        )}

                        {comparison.comparison.language_comparison && (
                          <div style={{ marginBottom: '12px' }}>
                            <strong>{translate('comparison.languageComparison')}：</strong>
                            <p style={{ marginTop: '4px', marginLeft: '20px', whiteSpace: 'pre-wrap' }}>
                              {comparison.comparison.language_comparison}
                            </p>
                          </div>
                        )}

                        {comparison.comparison.fine_motor_comparison && (
                          <div style={{ marginBottom: '12px' }}>
                            <strong>{translate('comparison.fineMotorComparison')}：</strong>
                            <p style={{ marginTop: '4px', marginLeft: '20px', whiteSpace: 'pre-wrap' }}>
                              {comparison.comparison.fine_motor_comparison}
                            </p>
                          </div>
                        )}

                        {comparison.comparison.cognitive_comparison && (
                          <div style={{ marginBottom: '12px' }}>
                            <strong>{translate('comparison.cognitiveComparison')}：</strong>
                            <p style={{ marginTop: '4px', marginLeft: '20px', whiteSpace: 'pre-wrap' }}>
                              {comparison.comparison.cognitive_comparison}
                            </p>
                          </div>
                        )}

                        {comparison.comparison.overall_gap && (
                          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f8d7da', borderRadius: '4px' }}>
                            <strong>{translate('comparison.overallGap')}：</strong>
                            <p style={{ marginTop: '4px', whiteSpace: 'pre-wrap' }}>
                              {comparison.comparison.overall_gap}
                            </p>
                          </div>
                        )}
                      </div>
                    )}

                    {comparison.recommendations && comparison.recommendations.length > 0 && (
                      <div style={{ padding: '16px', backgroundColor: '#d1ecf1', borderRadius: '4px' }}>
                        <h3 style={{ marginBottom: '12px', color: '#0c5460' }}>💡 {translate('comparison.suggestions')}</h3>
                        <ul style={{ marginLeft: '20px' }}>
                          {comparison.recommendations.map((rec, idx) => (
                            <li key={idx} style={{ marginBottom: '8px' }}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* 发育里程碑预测 */}
            {activeTab === 'milestones' && (
            <div className="card">
              <h2>{translate('milestones.title')}</h2>
              {milestones.length > 0 ? (
                <div style={{ marginTop: '20px' }}>
                  <textarea
                    readOnly
                    value={milestones.map((milestone, idx) => {
                      let text = `【${translate('milestones.milestone')} ${idx + 1}】\n`;
                      text += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
                      text += `📌 ${translate('milestones.milestone')}${language === 'zh' ? '名称' : ' Name'}：${milestone.milestone}\n\n`;
                      text += `⏰ ${translate('milestones.expectedTime')}：${milestone.expected_age_months} ${translate('comparison.months')}\n\n`;
                      
                      if (milestone.normal_age_range) {
                        text += `📊 ${translate('milestones.normalAgeRange')}：${milestone.normal_age_range}\n\n`;
                      }
                      
                      if (milestone.description) {
                        text += `📝 ${translate('milestones.description')}：\n${milestone.description}\n\n`;
                      }
                      
                      if (milestone.prediction_basis) {
                        text += `🔍 ${translate('milestones.predictionBasis')}：\n${milestone.prediction_basis}\n\n`;
                      }
                      
                      if (milestone.suggestions) {
                        text += `💡 ${translate('milestones.suggestions')}：\n${milestone.suggestions}\n\n`;
                      }
                      
                      text += `\n`;
                      return text;
                    }).join('\n')}
                    style={{
                      width: '100%',
                      minHeight: '400px',
                      maxHeight: '600px',
                      padding: '16px',
                      fontSize: '14px',
                      lineHeight: '1.6',
                      fontFamily: 'monospace',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      backgroundColor: '#f8f9fa',
                      resize: 'vertical',
                      overflowY: 'auto',
                      whiteSpace: 'pre-wrap',
                      color: '#333'
                    }}
                  />
                </div>
              ) : (
                <p style={{ marginTop: '20px', color: '#666' }}>{translate('milestones.noData')}</p>
              )}
            </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
