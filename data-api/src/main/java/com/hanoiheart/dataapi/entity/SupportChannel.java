package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

/**
 * Kênh đặt khám / hỗ trợ (web, hotline, fanpage, zalo, emergency).
 */
@Entity
@Table(name = "support_channels", schema = "hospital")
public class SupportChannel extends BaseEntity {

    /** web | zalo | hotline | fanpage | emergency | charity. */
    @Column(name = "channel_type", nullable = false, length = 32)
    private String channelType;

    @Column(name = "label", nullable = false)
    private String label;

    @Column(name = "url")
    private String url;

    @Column(name = "phone", length = 32)
    private String phone;

    @Column(name = "campus")
    private String campus;

    @Column(name = "sort_order")
    private Integer sortOrder;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = Boolean.TRUE;

    public String getChannelType() { return channelType; }
    public void setChannelType(String c) { this.channelType = c; }
    public String getLabel() { return label; }
    public void setLabel(String l) { this.label = l; }
    public String getUrl() { return url; }
    public void setUrl(String u) { this.url = u; }
    public String getPhone() { return phone; }
    public void setPhone(String p) { this.phone = p; }
    public String getCampus() { return campus; }
    public void setCampus(String c) { this.campus = c; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer s) { this.sortOrder = s; }
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean a) { this.isActive = a; }
}
